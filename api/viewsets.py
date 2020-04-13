import threading

from django.conf import settings
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, mixins
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404

from api import serializers as ss
from core.models import Country, Region, Checkpoint, CheckpointPass, Person, CITIZENSHIPS_KZ, CITIZENSHIP_KZ, Marker, \
    User
from core.service import DMEDService
from core.validators import is_iin
import logging


log = logging.getLogger(__name__)


class DjangoStrictModelPermissions(permissions.DjangoModelPermissions):
    """с проверкой на разрешение на просмотр модели"""
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class InspectorViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ss.InspectorSerializer
    queryset = User.objects.filter(groups__name='inspectors')

    def get_object(self):
        if self.request.user.groups.filter(name='inspectors').exists():
            return self.request.user
        raise Http404


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """Все страны"""
    queryset = Country.objects.all()
    serializer_class = ss.CountrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['$name']


class RegionViewSet(viewsets.ModelViewSet):
    """Все регионы"""
    queryset = Region.objects.all().order_by('-add_date')
    serializer_class = ss.RegionSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [SearchFilter]
    search_fields = ['^name']


class CheckpointViewSet(viewsets.ModelViewSet):
    """Все КПП"""
    queryset = Checkpoint.objects.all().order_by('-add_date')
    serializer_class = ss.CheckPointSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['region']
    search_fields = ['^name', '^region__name']


class CheckpointPassViewSet(viewsets.ModelViewSet):
    """Запись о прохождении КПП"""
    queryset = CheckpointPass.objects.all().order_by('-add_date')
    serializer_class = ss.CheckPointPassSerializer
    permission_classes = [DjangoStrictModelPermissions]


class PersonViewSet(viewsets.ModelViewSet):
    """Анкета человека"""
    queryset = Person.objects.all().order_by('-add_date')
    serializer_class = ss.PersonSerializer
    permission_classes = [permissions.IsAuthenticated, DjangoStrictModelPermissions]
    filter_backends = [SearchFilter]
    search_fields = ['$full_name']

    def get_queryset(self):
        # фильтрация только по иин, вручную
        q = super(PersonViewSet, self).get_queryset()
        if self.request.query_params.get('iin'):
            return q.filter(doc_id=self.request.query_params['iin'], citizenship__in=CITIZENSHIPS_KZ)
        return q

    def get_object(self):
        """Получение объекта по ИИН или id"""
        queryset = self.filter_queryset(self.get_queryset())

        if is_iin(self.kwargs[self.lookup_field]):
            filter_kwargs = {'doc_id': self.kwargs['pk'], 'citizenship__in': CITIZENSHIPS_KZ}
        else:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):  # legacy GET /api/person/{pk}
        """запрос анкеты по иин или ID
        если анкета не существует - создастся автоматически, и наполнится данными из Дамумед"""
        if not is_iin(kwargs['pk']):
            return super(PersonViewSet, self).retrieve(request, *args, **kwargs)

        # это ИИН
        # находим существующую или создаём свежую анкету
        p, created = Person.objects.get_or_create(
            doc_id=kwargs['pk'],
            citizenship__in=CITIZENSHIPS_KZ,
            defaults={
                'citizenship': Country.objects.get(pk=CITIZENSHIP_KZ)
            }
        )
        if p.dmed_id:
            # инфа уже была получена, не делаем внешний запрос
            return super(PersonViewSet, self).retrieve(request, *args, **kwargs)

        # ищем в dmed и сохраняем
        # запускаем параллельно
        threads = []
        for region in Region.objects.filter(dmed_url__isnull=False).order_by('dmed_priority'):
            t = threading.Thread(target=self.update_person_from_damu, args=(p, region))
            threads.append(t)

        while threads:
            # запускаем поиск в 2 потока
            chunk, threads = threads[:2], threads[2:]
            for t in chunk:
                t.start()

            # ждём когда закончат
            for t in chunk:
                t.join()
                if p.dmed_id:
                    break

            if p.dmed_id:
                break

        # возвращаем как есть
        return super(PersonViewSet, self).retrieve(request, *args, **kwargs)

    @staticmethod
    def update_person_from_damu(p: Person, region: Region):
        dmed = DMEDService(url=region.dmed_url, username=settings.DMED_LOGIN, password=settings.DMED_PASSWORD)
        updated = dmed.update_person(p)
        if updated:
            # если апдейт успешен, сохраняем анкету
            p.dmed_region = region  # запомним откуда получили информацию
            p.save()
            updated = dmed.update_person_detail(p)
            if updated:
                p.save()
            dmed.update_person_markers(p)

    def update(self, request, *args, **kwargs):
        log.info(f'rq body: {request.body}')
        return super(PersonViewSet, self).update(request, *args, **kwargs)

    def perform_update(self, serializer):  # PUT/PATCH /api/person/{pk}
        # запрещаем обновление базовых данных
        d = serializer.validated_data
        i = serializer.instance
        for f in ['doc_id', 'citizenship', 'full_name', 'sex', 'birth_date', 'first_name', 'second_name', 'last_name']:
            if getattr(i, f) and f in d:  # если в модели уже есть что-то в этом поле - запрещаем его обновление
                del d[f]
        return super(PersonViewSet, self).perform_update(serializer)

    def perform_create(self, serializer):  # POST /api/person
        serializer.validated_data['doc_id'] = serializer.validated_data.pop('iin', None)
        serializer.save()


class PersonMarkerViewSet(viewsets.ModelViewSet):
    """Все маркеры анкеты человека"""
    queryset = Marker.objects.all().order_by('-add_date')
    serializer_class = ss.MarkerSerializer
    permission_classes = [DjangoStrictModelPermissions]
