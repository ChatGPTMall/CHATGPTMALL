from rest_framework import serializers

from engine.models import PlanType, Community
from homelinked.models import HomePlans, HomepageNewFeature, CreditsHistory


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
    total_members = serializers.IntegerField(read_only=True)

    class Meta:
        model = Community
        fields = (
            "community_id",
            "name",
            "logo",
            "total_members"
        )


class GetCreditsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditsHistory
        exclude = (
            "id",
            "user"
        )


class CommunitiesJoinViewSerializer(serializers.ModelSerializer):
    total_members = serializers.IntegerField(read_only=True)
    has_joined = serializers.BooleanField(read_only=True)

    class Meta:
        model = Community
        fields = (
            "community_id",
            "name",
            "logo",
            "total_members",
            "has_joined"
        )