from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter

from core.models import Person, DMEDPersonInfo, CheckpointPass, Checkpoint, Place, Region, User
from core.service import DMEDService
from django.conf import settings
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


class DMEDPersonInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """Данные о людях в dmed"""
    queryset = DMEDPersonInfo.objects.all().order_by('-add_date')
    serializer_class = DMEDPersonInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            return super(DMEDPersonInfoViewSet, self).retrieve(request, *args, **kwargs)
        except Http404:
            u: User = request.user
            regions = []
            q = Region.objects.filter(dmed_url__isnull=False).order_by('dmed_priority')
            if u.region:
                q = q.exclude(u.region.id)
                regions.append(u.region)
            regions.extend(q)

            for region in regions:
                dmed = DMEDService(url=region.dmed_url, username=settings.DMED_LOGIN, password=settings.DMED_PASSWORD)
                r = dmed.get_person(kwargs['pk'])

                if r:
                    r.save()
                    try:
                        p = Person.objects.get(iin=kwargs['pk'])
                    except Person.DoesNotExist:
                        p = Person()
                    p.dmed_update(r)
                    p.save()

                    for m in dmed.get_markers(r):
                        r.markers.create(marker_id=m['markerID'], name=m['markerName'])
                    break

            return super(DMEDPersonInfoViewSet, self).retrieve(request, *args, **kwargs)


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
