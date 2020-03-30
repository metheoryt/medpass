from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, mixins, views, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from core.models import Person, DMEDPersonInfo, CheckpointPass, Checkpoint, Place, Region, User  # , ForeignVisit
from core.service import DMEDService
from django.conf import settings
from . import serializers as ss


class InspectorView(views.APIView):
    """Инспекторы"""
    queryset = User.objects.filter(groups__name='inspectors')
    serializer_class = ss.InspectorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)


class InspectorDetail(views.APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self):
        try:
            return User.objects.filter(groups__name='inspectors').get(pk=self.request.user.id)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        snippet = self.get_object()
        serializer = ss.InspectorSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, format=None):
        snippet = self.get_object()
        serializer = ss.InspectorSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ForeignVisitViewSet(viewsets.ModelViewSet):
#     """Посещение лицами других стран"""
#     queryset = ForeignVisit.objects.all().order_by('-add_date')
#     serializer_class = ss.ForeignVisitSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     filterset_fields = ['country']
#     search_fields = ['^country']


class PersonViewSet(viewsets.ModelViewSet):
    """Люди"""
    queryset = Person.objects.all().order_by('-add_date')
    serializer_class = ss.PersonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['iin']
    search_fields = ['^full_name']


class DMEDPersonInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """Данные о людях в dmed"""
    queryset = DMEDPersonInfo.objects.all().order_by('-add_date')
    serializer_class = ss.DMEDPersonInfoSerializer
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
    serializer_class = ss.CheckPointPassSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = Checkpoint.objects.all().order_by('-add_date')
    serializer_class = ss.CheckPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['region']
    search_fields = ['^name', '^region__name']


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all().order_by('-add_date')
    serializer_class = ss.PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['^address', '^region__name']


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all().order_by('-add_date')
    serializer_class = ss.RegionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['^name']
