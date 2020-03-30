from rest_framework import serializers

from core import models
from core.models import Region


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Person
        fields = '__all__'
        read_only_fields = ['dmed_info']


class DMEDPersonInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DMEDPersonInfo
        fields = ['iin', 'id', 'rpn_id', 'person', 'markers', 'nationality_id', 'citizenship_id']


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'country', 'name']


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
        fields = ['id', 'name', 'location', 'region']


class InspectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = 'id', 'username', 'checkpoint'
        read_only_fields = 'id', 'username'


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Place
        fields = ['region', 'address', 'contact_number']

    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())
