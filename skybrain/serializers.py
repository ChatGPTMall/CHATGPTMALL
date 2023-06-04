from rest_framework import serializers

from skybrain.models import LicensesRequests, Room


class LicensesViewSerializer(serializers.ModelSerializer):
    no_of_licenses = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = LicensesRequests
        exclude = (
            "added_on",
        )


class CreateLicensesViewSerializer(serializers.Serializer):
    organization = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    csv_file = serializers.FileField(required=True)


class OrganizationRoomsSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Room
        exclude = (
            "room_key",
            "organization",
            "id",
            "added_on",
        )
        read_only_fields = (
            "organization_name",
        )

    def get_organization_name(self, room):
        return room.organization.name


class SkybrainCustomerRoomSerializer(serializers.Serializer):
    organization = serializers.CharField(required=True)
    room_id = serializers.CharField(required=True)
    room_key = serializers.CharField(required=True)