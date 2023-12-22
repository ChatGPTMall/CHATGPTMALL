from rest_framework import serializers

from engine.models import Category, Items, FeedComments, CommunityPosts
from homelinked.serializers import ItemShortSerializer


class TextToTexTViewSerializer(serializers.Serializer):
    input = serializers.CharField(required=True)


class VisionViewSerializer(serializers.Serializer):
    input = serializers.CharField(required=True)
    image = serializers.ImageField(required=True)

class TextToTexTViewImageSerializer(serializers.Serializer):
    input = serializers.CharField(required=True)


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


class PostLikeViewSerializer(serializers.Serializer):
    post_id = serializers.UUIDField(required=True)
    like = serializers.IntegerField(min_value=0, max_value=1, required=True, help_text="like value should 0 or 1")


class PostCommentViewSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FeedComments
        exclude = (
            "id",
            "parent",
            "user",
            "post"
        )
        read_only_fields = (
            "email",
            "name"
        )

    def get_email(self, comment):
        return str(comment.user.email)

    def get_name(self, comment):
        return comment.user.get_full_name()


class GetPostsViewSerializer(serializers.Serializer):
    item_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CommunityPosts
        exclude = (
            "id",
            "user",
            "added_on",
            "community",
            "item",
        )
        read_only_fields = (
            "item_details",
        )

    def get_item_details(self, post):
        return ItemShortSerializer(post.item).data
