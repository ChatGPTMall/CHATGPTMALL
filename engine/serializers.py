from rest_framework import serializers

from engine.models import Category, Items


class TextToTexTViewSerializer(serializers.Serializer):
    input = serializers.CharField(required=True)
    image = serializers.ImageField(required=True)


class ImageAnalysisViewSerializer(serializers.Serializer):
    image_url = serializers.CharField(required=True)


class ShopItemsViewSerializer(serializers.Serializer):
    category = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    communities = serializers.JSONField(required=True)
    image = serializers.ImageField(required=True)
    price = serializers.IntegerField(required=True)


class GetItemsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = "__all__"


class ShopCategoriesViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class TextToTexTMicrosoftViewSerializer(serializers.Serializer):
    input = serializers.CharField(required=True)
    endpoint = serializers.CharField(required=True)
    ms_key = serializers.CharField(required=True)


class TranscribeAudioSerializer(serializers.Serializer):
    audio = serializers.FileField(required=True)