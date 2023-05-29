from rest_framework import serializers

from skybrain.models import LicensesRequests


class LicensesViewSerializer(serializers.ModelSerializer):
    no_of_licenses = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = LicensesRequests
        exclude = (
            "added_on",
        )