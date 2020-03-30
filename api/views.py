from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter

from core.models import Person, DMEDPersonInfo, CheckpointPass, Checkpoint, Place, Region
from .serializers import PersonSerializer, DMEDPersonInfoSerializer, CheckPointPassSerializer, CheckPointSerializer, \
    PlaceSerializer, RegionSerializer


class PersonViewSet(viewsets.ModelViewSet):
    """Люди"""
    queryset = Person.objects.all().order_by('-add_date')
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['iin']
    search_fields = ['^full_name']


class DMEDPersonInfoViewSet(viewsets.ModelViewSet):
    """Данные о них в dmed (только для чтения и создания через сабмит ИИН)"""
    queryset = DMEDPersonInfo.objects.all().order_by('-add_date')
    serializer_class = DMEDPersonInfoSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckpointPassViewSet(viewsets.ModelViewSet):
    """запись о прохождении пропускного пункта"""
    queryset = CheckpointPass.objects.all().order_by('-add_date')
    serializer_class = CheckPointPassSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = Checkpoint.objects.all().order_by('-add_date')
    serializer_class = CheckPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['^name', '^region__name']


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all().order_by('-add_date')
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['^address', '^region__name']


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all().order_by('-add_date')
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['^name']
