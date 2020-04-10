from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from rest_framework import mixins, permissions, viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from api.viewsets import DjangoStrictModelPermissions
from core import models
from core.models import CheckpointPass
from . import serializers as ss


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
        page_size = 5
        page_size_query_param = 'page_size'
        max_page_size = 100

    serializer_class = ss.CheckPointPassSerializer
    permission_classes = [DjangoStrictModelPermissions]
    pagination_class = Pagination

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

    def get_queryset(self):
        return models.PersonPassData.objects.filter(
            checkpoint_pass__checkpoint=self.request.user.checkpoint,
            checkpoint_pass=self.kwargs['checkpoint_pass_pk']
        ).order_by('-add_date')

    def perform_create(self, serializer):
        serializer.validated_data['checkpoint_pass'] = models.CheckpointPass.objects.get(pk=self.kwargs['checkpoint_pass_pk'])
        serializer.save()


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
    queryset = models.Vehicle.objects.all().order_by('-add_date')
    serializer_class = ss.VehicleSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ['^grnz']
    lookup_field = 'grnz'


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """Страны"""
    queryset = models.Country.objects.all().order_by('priority', 'name')
    serializer_class = ss.CountrySerializer
    permission_classes = [permissions.IsAuthenticated]


class CountryPersonViewSet(viewsets.ModelViewSet):
    """Анкета гражданина конкретной страны"""
    serializer_class = ss.PersonSerializer
    permission_classes = [permissions.IsAuthenticated, DjangoStrictModelPermissions]
    lookup_field = 'doc_id'

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
    serializer_class = ss.CameraCaptureSerializer
    permission_classes = [DjangoStrictModelPermissions]
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        # Захваты с камер, относящихся к текущему КПП
        # по которым ещё не был проведён досмотр
        return models.CameraCapture.objects.filter(
            Q(camera__checkpoint=self.request.user.checkpoint),
            Q(checkpoint_pass__status=models.CheckpointPass.Status.NOT_PASSED) | Q(checkpoint_pass__isnull=True),
        ).order_by('date')

    @action(detail=True, methods=['get'], url_path='pass')
    def checkpoint_pass(self, request, pk=None):
        capture: models.CameraCapture = self.get_object()
        if not capture.checkpoint_pass:
            p = models.CheckpointPass()
            p.vehicle = capture.vehicle
            p.checkpoint = self.request.user.checkpoint
            p.inspector = self.request.user
            p.save()
            capture.checkpoint_pass = p
            capture.save()
        return redirect('inspector-checkpoint-pass-detail', pk=capture.checkpoint_pass.id)
