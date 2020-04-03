from django.conf import settings
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, views, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from core.models import Person, CheckpointPass, Checkpoint, Region, User, Marker, Country
from core.service import DMEDService
from . import serializers as ss
from django.db.models import Q


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


class InspectorDetail(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(groups__name='inspectors')

    def get_object(self):
        return self.request.user

    def get(self, request, format=None):
        user = self.get_object()
        serializer = ss.InspectorSerializer(user, context={'request': request})
        return Response(serializer.data)

    def put(self, request, format=None):
        user = self.get_object()
        serializer = ss.InspectorSerializer(user, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonViewSet(viewsets.ModelViewSet):
    """Люди"""
    queryset = Person.objects.all().order_by('-add_date')
    serializer_class = ss.PersonSerializer
    permission_classes = [permissions.IsAuthenticated, DjangoStrictModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['birth_date']
    search_fields = ['$full_name']

    def get_object(self):
        # получает Person по id или iin
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = self.kwargs[lookup_url_kwarg]

        queryset = queryset.filter(Q(id=pk) | Q(iin=pk))

        obj = get_object_or_404(queryset)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def retrieve(self, request, *args, **kwargs):
        try:
            # пытаемся найти существующий
            return super(PersonViewSet, self).retrieve(request, *args, **kwargs)
        except Http404:
            # ищем в dmed и сохраняем
            # формируем список регионов, по которым будем искать
            u: User = request.user
            regions = []
            q = Region.objects.filter(dmed_url__isnull=False).order_by('dmed_priority')
            if u.checkpoint:
                q = q.exclude(id=u.checkpoint.region.id)
                regions.append(u.checkpoint.region)  # регион КПП будет запрошен в первую очередь
            regions.extend(q)

            # создаём свежий объект
            p = Person()
            p.iin = kwargs['pk']
            # ищем в цикле пока не найдём
            for region in regions:
                dmed = DMEDService(url=region.dmed_url, username=settings.DMED_LOGIN, password=settings.DMED_PASSWORD)
                p = dmed.update_person(p)

                if p:
                    # если апдейт успешен, сохраняем анкету
                    p.dmed_region = region  # запомним откуда получили информацию
                    p.save()
                    dmed.update_person_markers(p)
                    break
            # возвращаем как есть
            return super(PersonViewSet, self).retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        # запрещаем обновление базовых данных
        d = serializer.validated_data
        i = serializer.instance
        for f in ['full_name', 'sex', 'birth_date', 'iin', 'first_name', 'second_name', 'last_name']:
            if getattr(i, f) and d.get(f):
                del d[f]
        return super(PersonViewSet, self).perform_update(serializer)


class PersonMarkerViewSet(viewsets.ModelViewSet):
    """Маркеры"""
    queryset = Marker.objects.all().order_by('-add_date')
    serializer_class = ss.MarkerSerializer
    permission_classes = [DjangoStrictModelPermissions]


class CheckpointPassViewSet(viewsets.ModelViewSet):
    """запись о прохождении пропускного пункта"""
    queryset = CheckpointPass.objects.all().order_by('-add_date')
    serializer_class = ss.CheckPointPassSerializer
    permission_classes = [DjangoStrictModelPermissions]


class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = Checkpoint.objects.all().order_by('-add_date')
    serializer_class = ss.CheckPointSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['region']
    search_fields = ['^name', '^region__name']


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all().order_by('-add_date')
    serializer_class = ss.RegionSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [SearchFilter]
    search_fields = ['^name']


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.distinct('name', 'priority')
    serializer_class = ss.CountrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['$name']
