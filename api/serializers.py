from django.conf import settings
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from core import models
from core.models import User, Region, Person
from core.service import DMEDService


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Person
        fields = ['full_name', 'birth_date', 'sex',
                  'iin', 'first_name', 'second_name',
                  'last_name', 'contact_number', 'dmed_info', 'add_date']
        read_only_fields = ['dmed_info']


class DMEDPersonInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DMEDPersonInfo
        fields = ['iin',    'id', 'person', 'markers']
        read_only_fields = ['id', 'person', 'markers']

    def create(self, validated_data):
        u: User = self.context['request'].user
        regions = []
        q = Region.objects.filter(dmed_url__isnull=False).order_by('dmed_priority')
        if u.region:
            q = q.exclude(u.region.id)
            regions.append(u.region)
        regions.extend(q)

        for region in regions:
            dmed = DMEDService(url=region.dmed_url, username=settings.DMED_LOGIN, password=settings.DMED_PASSWORD)
            r = dmed.get_person(validated_data['iin'])
            if r:
                r.save()
                for m in dmed.get_markers(r):
                    try:
                        r.markers.create(marker_id=m['markerID'], name=m['markerName'])
                    except IntegrityError:
                        pass
                try:
                    p = r.person
                except models.DMEDPersonInfo.person.RelatedObjectDoesNotExist:
                    try:
                        p = Person.objects.get(iin=r.iin)
                    except Person.DoesNotExist:
                        p = Person()
                p.dmed_update(r)
                p.save()
                return r
            else:
                raise NotFound()


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['country', 'name']


class CheckPointPassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CheckpointPass
        fields = ['date', 'person', 'checkpoint',
                  'source_place', 'destination_place']
        depth = 1


class CheckPointSerializer(serializers.HyperlinkedModelSerializer):
    """Контрольно-пропускной пост"""
    class Meta:
        model = models.Checkpoint
        fields = ['name', 'location', 'region']

    # region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Place
        fields = ['region', 'address', 'contact_number']

    # region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())
