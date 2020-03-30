from django.conf import settings
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, mixins
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from core.models import Person, User, Region, DMEDPersonInfo
from core.service import DMEDService
from .serializers import PersonSerializer, DMEDPersonInfoSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by('-add_date')
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated]


class DMEDPersonInfoViewSet(viewsets.ModelViewSet):
    queryset = DMEDPersonInfo.objects.all().order_by('-add_date')
    serializer_class = DMEDPersonInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
