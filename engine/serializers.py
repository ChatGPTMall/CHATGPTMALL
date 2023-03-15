from rest_framework import serializers


class TextToTexTViewSerializer(serializers.Serializer):
    input = serializers.CharField(required=True)