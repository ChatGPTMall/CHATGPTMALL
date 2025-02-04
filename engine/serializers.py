from rest_framework import serializers

from engine.models import Category, Items, FeedComments, CommunityPosts, Chatbots, WhatsappConfiguration, \
    WeChatOfficialConfiguration, CouponCode
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


class ItemsBulkCreateSerializer(serializers.Serializer):
    item_type = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    image = serializers.ImageField(required=True)
    price = serializers.FloatField(required=True)
    location = serializers.CharField(required=True)
    stock = serializers.IntegerField(required=True)
    public_bank = serializers.IntegerField(required=True)
    category = serializers.IntegerField(required=True)



class NetworkPostItemSessionCheckoutSerializer(serializers.Serializer):
    item_id = serializers.UUIDField(required=True)
    total_price = serializers.IntegerField(required=True)
    success_url = serializers.URLField(required=True)
    cancel_url = serializers.URLField(required=True)


class ChatbotAPIViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatbots
        exclude = (
            "id",
            "user"
        )


class WhatsappConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsappConfiguration
        exclude = (
            "chatbot",
        )


class WeChatListingAPIViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = "__all__"


class WeChatConfigurationAPIViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeChatOfficialConfiguration
        exclude = (
            "id",
        )


class CreateCouponAPIViewSeralizer(serializers.ModelSerializer):
    community_name = serializers.CharField(read_only=True)
    price = serializers.IntegerField(read_only=True)

    class Meta:
        model = CouponCode
        exclude = (
            "id",
        )
        read_only_fields = (
            "community_name",
            "price"
        )