from rest_framework import serializers

from core import models
from core.models import Region, Person, Country


class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Marker
        fields = ['id', 'url', 'name', 'persons']


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = [
            'id',
            'iin',
            'citizenship',
            'full_name',
            'sex',
            'birth_date',
            'last_name',
            'first_name',
            'second_name',
            'contact_numbers',
            'residence_place',
            'study_place',
            'working_place',
            'had_contact_with_infected',
            'been_abroad_last_month',
            'extra',
            'dmed_id',
            'dmed_rpn_id',
            'dmed_master_data_id',
            'dmed_region',
            'url',
            'markers'
        ]
        read_only_fields = [
            'dmed_id', 'dmed_rpn_id', 'dmed_master_data_id', 'dmed_region', 'temperature'
        ]

    citizenship = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    iin = serializers.CharField(label='ИИН / ID документа', required=False)
    url = serializers.HyperlinkedIdentityField(view_name='person-detail', read_only=True)
    markers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'country', 'name']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ['id', 'name']


class CheckPointPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CheckpointPass
        fields = [
            'id',
            'person',  # legacy
            'source_place',
            'destination_place',
            'add_date',
            'checkpoint',
            'inspector',
        ]
        read_only_fields = ['add_date', 'inspector', 'checkpoint']

    person = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())

    def create(self, validated_data):
        # legacy: работаем со списком анкет как с одной анкетой
        # игнорируем температуру
        validated_data['persons'] = [validated_data.pop('person')]
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
