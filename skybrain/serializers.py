from rest_framework import serializers

from skybrain.models import LicensesRequests, Room, RoomHistory, RoomItems, Organization, CustomerSupport


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


class HistoryRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoomHistory
        exclude = (
            "id",
            "room"
        )


class ItemsRoomViewSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    video = serializers.FileField(required=True)
    price = serializers.IntegerField(required=True)
    description = serializers.CharField(required=True)
    is_private = serializers.BooleanField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        model = RoomItems
        exclude = (
            "id",
            "added_on",
        )


class OrganizationsviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        exclude = (
            "id",
            "added_on"
        )


class CSQueriesViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSupport
        exclude = (
            "room",
        )


class CSQueriesUpdateViewSerializer(serializers.Serializer):
    reply = serializers.CharField(required=True)
    query_id = serializers.IntegerField(required=True)