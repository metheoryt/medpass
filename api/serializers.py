from rest_framework import serializers

from core import models
from core.models import Region


# class ForeignVisitSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = models.ForeignVisit
#         fields = '__all__'


class InspectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = 'id', 'username', 'checkpoint'
        read_only_fields = 'id', 'username'


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Person
        fields = ['full_name', 'birth_date', 'sex',
                  'iin', 'first_name', 'second_name',
                  'last_name', 'contact_numbers', 'dmed_info', 'add_date', 'foreign_visits']
        read_only_fields = ['dmed_info', 'foreign_visits']


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

    # region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Place
        fields = ['region', 'address', 'contact_number']

    # region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())
