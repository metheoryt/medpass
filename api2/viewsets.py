from datetime import datetime

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from rest_framework import mixins, permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from api.viewsets import DjangoStrictModelPermissions
from core import models
from core.models import CheckpointPass, CITIZENSHIPS_KZ
from core.service import DMEDService
from . import serializers as ss
import logging

log = logging.getLogger(__name__)


class InspectorViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ss.InspectorSerializer
    queryset = models.User.objects.filter(groups__name='inspectors')

    def get_object(self):
        if self.request.user.groups.filter(name='inspectors').exists():
            return self.request.user
        raise Http404


class InspectorCheckpointViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """КПП текущего инспектора"""
    queryset = models.Checkpoint.objects.all().order_by('-add_date')
    serializer_class = ss.CheckPointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.groups.filter(name='inspectors').exists():
            return self.request.user.checkpoint
        raise Http404


class InspectorCheckpointPassViewSet(viewsets.ModelViewSet):
    """записи о прохождении КПП, на котором находится мединспектор"""
    class Pagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = 'page_size'
        max_page_size = 100

    pagination_class = Pagination
    serializer_class = ss.CheckPointPassSerializer
    permission_classes = [DjangoStrictModelPermissions]

    def get_queryset(self):
        # сначала непроверенные, начиная с самых старых
        return CheckpointPass.objects.filter(
            checkpoint=self.request.user.checkpoint,
        ).order_by('status', 'add_date')

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.inspector = self.request.user
        instance.checkpoint = self.request.user.checkpoint
        instance.save()
        return instance


class CheckpointPassPersonViewSet(viewsets.ModelViewSet):
    serializer_class = ss.PersonPassDataSerializer
    permission_classes = [DjangoStrictModelPermissions]
    lookup_field = 'person__id'

    def get_queryset(self):
        return models.PersonPassData.objects.filter(
            checkpoint_pass__checkpoint=self.request.user.checkpoint,
            checkpoint_pass=self.kwargs['checkpoint_pass_pk']
        ).order_by('-add_date')

    def perform_create(self, serializer):
        p, created = models.Person.objects.get_or_create(
            **serializer.validated_data['person']
        )
        models.PersonPassData.objects.update_or_create(
            person=p,
            checkpoint_pass_id=self.kwargs['checkpoint_pass_pk'],
            defaults={'temperature': serializer.validated_data['temperature']}
        )


class RegionViewSet(viewsets.ModelViewSet):
    """Регионы"""
    queryset = models.Region.objects.all().order_by('name')
    serializer_class = ss.RegionSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class CheckpointViewSet(viewsets.ModelViewSet):
    """КПП"""
    queryset = models.Checkpoint.objects.all().order_by('name')
    serializer_class = ss.CheckPointSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class VehicleViewSet(viewsets.ModelViewSet):
    """Автомобили"""
    class Pagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = 'page_size'
        max_page_size = 100

    pagination_class = Pagination

    queryset = models.Vehicle.objects.all().order_by('-add_date')
    serializer_class = ss.VehicleSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^grnz']
    lookup_field = 'grnz'


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """Страны"""
    queryset = models.Country.objects.all()
    serializer_class = ss.CountrySerializer
    permission_classes = [permissions.IsAuthenticated]


class CountryPersonViewSet(viewsets.ModelViewSet):
    """Анкета гражданина конкретной страны"""
    class Pagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = 'page_size'
        max_page_size = 100

    pagination_class = Pagination

    serializer_class = ss.PersonSerializer
    permission_classes = [permissions.IsAuthenticated, DjangoStrictModelPermissions]
    lookup_field = 'doc_id'

    def retrieve(self, request, *args, **kwargs):
        if request.query_params.get('fetch') and int(kwargs['country_pk']) in CITIZENSHIPS_KZ:
            # Если запрашивают казахстанца, обновляем анкету из DAMU, создаём если таковой нет
            p, created = models.Person.objects.get_or_create(
                doc_id=kwargs['doc_id'],
                citizenship__in=CITIZENSHIPS_KZ,
                defaults={
                    'citizenship': models.Country.objects.get(pk=kwargs['country_pk'])
                }
            )
            if p.dmed_id:
                # инфа уже была получена, не делаем внешний запрос
                return super(CountryPersonViewSet, self).retrieve(request, *args, **kwargs)

            p.update_from_dmed()

        return super(CountryPersonViewSet, self).retrieve(request, *args, **kwargs)

    def get_queryset(self):
        return models.Person.objects.filter(citizenship=self.kwargs['country_pk']).order_by('-add_date')

    def perform_create(self, serializer):
        serializer.validated_data['citizenship'] = models.Country.objects.get(pk=self.kwargs['country_pk'])
        return super(CountryPersonViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        return self.perform_create(serializer)


class CountryPersonMarkerViewSet(viewsets.ModelViewSet):
    """Все маркеры анкеты гражданина конкретной страны"""
    serializer_class = ss.PersonMarkerSerializer
    permission_classes = [DjangoStrictModelPermissions]

    def get_queryset(self):
        return models.Marker.objects.filter(
            persons__doc_id=self.kwargs['person_doc_id'],
            persons__citizenship=self.kwargs['country_pk']
        ).order_by('-add_date')


class CheckpointCameraCaptureViewSet(viewsets.ReadOnlyModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = 'page_size'
        max_page_size = 100

    pagination_class = Pagination

    serializer_class = ss.CameraCaptureSerializer
    permission_classes = [DjangoStrictModelPermissions]

    def get_queryset(self):
        # Захваты с камер, относящихся к текущему КПП
        # по которым ещё не был проведён досмотр
        q = models.CameraCapture.objects.filter(
            Q(camera__checkpoint=self.request.user.checkpoint),
            Q(checkpoint_pass__status=models.CheckpointPass.Status.NOT_PASSED) | Q(checkpoint_pass__isnull=True),
        ).order_by('-add_date')
        if self.request.query_params.get('ts_from'):
            dt_from = datetime.fromtimestamp(float(self.request.query_params['ts_from']))
            q = q.filter(date__gte=dt_from)
        return q

    @action(detail=True, methods=['get'], url_path='pass')
    def checkpoint_pass(self, request, pk=None):
        capture: models.CameraCapture = self.get_object()
        checkpoint_pass = capture.create_or_update_checkpoint_pass(self.request.user)
        return redirect('inspector-checkpoint-pass-detail', pk=checkpoint_pass.id)
