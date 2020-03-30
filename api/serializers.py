from rest_framework import serializers

from core import models
from core.models import Region


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = '__all__'

    url = serializers.HyperlinkedIdentityField(view_name='person-detail', read_only=True)
    dmed_info = serializers.HyperlinkedRelatedField(view_name='dmedpersoninfo-detail', read_only=True)


class DMEDPersonInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DMEDPersonInfo
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'country', 'name']


class CheckPointPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CheckpointPass
        fields = ['date', 'person', 'checkpoint',
                  'source_place', 'destination_place', 'inspector']
        read_only_fields = ['inspector']

    def create(self, validated_data):
        instance = super(CheckPointPassSerializer, self).create(validated_data)
        instance.inspector = self.context['request'].user
        instance.save()
        return instance


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
