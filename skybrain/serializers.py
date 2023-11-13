from rest_framework import serializers

from skybrain.models import LicensesRequests, Room, RoomItems, Organization, CustomerSupport, Favourites, \
    CustomInstructions
from users.models import RoomHistory


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
        if room.organization:
            return room.organization.name
        return None


class SkybrainCustomerRoomSerializer(serializers.Serializer):
    organization = serializers.CharField(required=False)
    room_id = serializers.CharField(required=True)
    room_key = serializers.CharField(required=True)


class HistoryRoomSerializer(serializers.ModelSerializer):
    is_favourite = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RoomHistory
        exclude = (
            "room",
            "user"
        )
        read_only_fields = (
            "is_favourite",
        )

    def get_is_favourite(self, history):
        if Favourites.objects.filter(history_id=history.id).exists():
            return True
        return False


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
            "added_on",
            "room",
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


class FavouritesViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourites
        exclude = (
            "updated_on",
            "room"
        )
        read_only_fields = (
            "room_key",
        )


class ItemsSendEmailViewSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)


class ShareRoomItemsSerializer(serializers.Serializer):
    rooms = serializers.JSONField(required=True)
    item_id = serializers.IntegerField(required=True)
    organization = serializers.CharField(required=True)


class ShareRoomResponseSerializer(serializers.Serializer):
    rooms = serializers.JSONField(required=True)
    history_id = serializers.IntegerField(required=True)
    organization = serializers.CharField(required=True)


class OCRImageUploadViewSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)


class urlOCRImageUploadViewSerializer(serializers.Serializer):
    image_url = serializers.URLField(required=True)


class UpdateRoomViewSerializer(serializers.Serializer):
    custom_instructions = serializers.BooleanField(required=True)


class CustomInstructionsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomInstructions
        exclude = (
            "updated_on",
            "room"
        )


class RoomAccessShareSerializer(serializers.Serializer):
    email = serializers.JSONField(required=True)
    room_key = serializers.CharField(required=True)
    user_type = serializers.CharField(required=True, help_text="visitor or contributor")

