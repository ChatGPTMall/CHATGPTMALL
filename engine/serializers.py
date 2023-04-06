from rest_framework import serializers


class TextToTexTViewSerializer(serializers.Serializer):
    input = serializers.CharField(required=True)


class ImageAnalysisViewSerializer(serializers.Serializer):
    image_url = serializers.CharField(required=True)