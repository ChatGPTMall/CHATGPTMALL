from rest_framework import serializers

from engine.models import Category


class TextToTexTViewSerializer(serializers.Serializer):
    input = serializers.CharField(required=True)


class ImageAnalysisViewSerializer(serializers.Serializer):
    image_url = serializers.CharField(required=True)


class ShopItemsViewSerializer(serializers.Serializer):
    category = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    image = serializers.ImageField(required=True)


class ShopCategoriesViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"