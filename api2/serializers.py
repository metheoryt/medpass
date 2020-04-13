from rest_framework import serializers

from core import models


class InspectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = 'username', 'checkpoint'
        read_only_fields = 'username',


class CheckPointSerializer(serializers.ModelSerializer):
    """Контрольно-пропускной пост"""
    class Meta:
        model = models.Checkpoint
        fields = '__all__'


class PersonPassDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersonPassData
        fields = ['id', 'person', 'temperature']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ['id', 'name']


class PersonMarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Marker
        fields = ['id', 'name']


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = '__all__'
        # fields = [
        #     'id',
        #     'doc_id',
        #     'citizenship',
        #     'full_name',
        #     'sex',
        #     'birth_date',
        #     'last_name',
        #     'first_name',
        #     'second_name',
        #     'contact_numbers',
        #     'residence_place',
        #     'study_place',
        #     'working_place',
        #     'had_contact_with_infected',
        #     'been_abroad_last_month',
        #     'extra',
        #     'dmed_id',
        #     'dmed_rpn_id',
        #     'dmed_master_data_id',
        #     'dmed_region',
        #     'markers'
        # ]
        read_only_fields = [
            'dmed_id', 'dmed_rpn_id', 'dmed_master_data_id', 'dmed_region', 'temperature'
        ]
    citizenship = serializers.PrimaryKeyRelatedField(queryset=models.Country.objects.all(), required=False)
    # markers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class CheckPointPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CheckpointPass
        fields = [
            'id',
            'checkpoint',
            'source_place',
            'destination_place',
            'add_date',
            'inspector',
            'persons',
            'vehicle',
            'direction',
            'status'
        ]
        read_only_fields = ['add_date', 'inspector', 'checkpoint', 'persons']
        # depth = 1

    persons = PersonSerializer(many=True, read_only=True)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = ['id', 'name']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vehicle
        fields = 'grnz', 'model'


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Camera
        fields = 'id', 'location'


class CameraCaptureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CameraCapture
        fields = 'id', 'date', 'add_date', 'camera', 'vehicle'

    vehicle = VehicleSerializer()
    camera = CameraSerializer()
