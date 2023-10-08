from rest_framework import serializers

from engine.models import PlanType
from homelinked.models import HomePlans


class HomePlansAPIViewSerializer(serializers.ModelSerializer):
    features = serializers.JSONField(required=True)
    price = serializers.IntegerField(required=True)

    class Meta:
        model = HomePlans
        exclude = (
            "id",
            "added_on",
            "updated_on",
        )