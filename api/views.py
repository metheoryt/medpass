from django.conf import settings
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, views, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from core.models import Person, DMEDPersonInfo, CheckpointPass, Checkpoint, Region, User
from core.service import DMEDService
from . import serializers as ss


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
    filterset_fields = ['iin']
    search_fields = ['^full_name']


class DMEDPersonInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """Данные о людях в dmed"""
    queryset = DMEDPersonInfo.objects.all().order_by('-add_date')
    serializer_class = ss.DMEDPersonInfoSerializer
    permission_classes = [permissions.IsAuthenticated, DjangoStrictModelPermissions]

    def retrieve(self, request, *args, **kwargs):
        try:
            return super(DMEDPersonInfoViewSet, self).retrieve(request, *args, **kwargs)
        except Http404:
            u: User = request.user
            regions = []
            q = Region.objects.filter(dmed_url__isnull=False).order_by('dmed_priority')
            if u.checkpoint:
                q = q.exclude(id=u.checkpoint.region.id)
                regions.append(u.checkpoint.region)
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
    permission_classes = [permissions.IsAuthenticated, DjangoStrictModelPermissions]


class CheckpointViewSet(viewsets.ModelViewSet):
    queryset = Checkpoint.objects.all().order_by('-add_date')
    serializer_class = ss.CheckPointSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['region']
    search_fields = ['^name', '^region__name']


# class PlaceViewSet(viewsets.ModelViewSet):
#     queryset = Place.objects.all().order_by('-add_date')
#     serializer_class = ss.PlaceSerializer
#     permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     filterset_fields = ['region']
#     search_fields = ['^address']


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all().order_by('-add_date')
    serializer_class = ss.RegionSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    filter_backends = [SearchFilter]
    search_fields = ['^name']
