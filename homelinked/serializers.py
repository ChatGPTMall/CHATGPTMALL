from rest_framework import serializers

from engine.models import PlanType, Community, CommunityPosts, Items, Purchases
from homelinked.models import HomePlans, HomepageNewFeature, CreditsHistory, WeChatAccounts


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


class ItemShortSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Items
        exclude = (
            "added_on",
            "vendor",
            "category",
            "public_bank",
            "private_bank",

        )
        read_only_fields = (
            "name",
        )

    def get_name(self, item):
        return item.vendor.get_full_name() if item.vendor else "Benny Liao"


class GrowthNetworkSerializer(serializers.ModelSerializer):
    item_details = serializers.SerializerMethodField(read_only=True)
    likes = serializers.SerializerMethodField(read_only=True)
    liked = serializers.SerializerMethodField(read_only=True)
    total_comments = serializers.SerializerMethodField(read_only=True)

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
            "likes",
            "liked",
            "total_comments",
        )

    def get_item_details(self, post):
        return ItemShortSerializer(post.item).data

    def get_likes(self, post):
        return post.post_likes.count()

    def get_liked(self, post):
        try:
            user = self.context["request"].user
        except KeyError:
            user = self.context["user"]
        if user.likes.filter(post=post).exists():
            return True
        return False

    def get_total_comments(self, post):
        return post.comments.count()


class RedeemCouponViewSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(required=True)


class ItemPurchasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchases
        exclude = (
            "updated_on",
            "user",
            "id",
        )


class WeChatAPIViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeChatAccounts
        exclude = (
            "added_on",
            "user",
            "id",
        )