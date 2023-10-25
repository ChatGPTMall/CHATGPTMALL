from rest_framework import serializers

from engine.models import PlanType, Community
from homelinked.models import HomePlans, HomepageNewFeature


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


class HomepageNewFeatureViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepageNewFeature
        exclude = (
            "id",
            "updated_on"
        )


class CommunitiesViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = (
            "name",
            "logo"
        )