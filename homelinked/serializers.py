from rest_framework import serializers

from homelinked.models import HomePlans


class HomePlansAPIViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePlans
        exclude = (
            "added_on",
            "updated_on",
        )