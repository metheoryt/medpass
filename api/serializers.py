from rest_framework import serializers

from core import models
from core.models import Region


class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Marker
        fields = ['id', 'url', 'name', 'persons']


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = '__all__'
        read_only_fields = [
            'dmed_id', 'dmed_rpn_id', 'dmed_master_data_id', 'dmed_region'
        ]

    url = serializers.HyperlinkedIdentityField(view_name='person-detail', read_only=True)
    markers = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Marker.objects.all())


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'country', 'name']


class CheckPointPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CheckpointPass
        fields = ['date', 'person', 'checkpoint',
                  'source_place', 'destination_place', 'inspector']
        read_only_fields = ['inspector', 'checkpoint']

    def create(self, validated_data):
        instance = super(CheckPointPassSerializer, self).create(validated_data)
        instance.inspector = self.context['request'].user
        instance.checkpoint = instance.inspector.checkpoint
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
