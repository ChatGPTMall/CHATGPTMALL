import io

import chardet
import pandas as pd
from django.contrib import admin
from engine.models import Items, Category, ResponsesDB, VoiceToVoiceRequests, ImagesDB, ShopAccess, Plans, Industries, \
    Jobs, Capabilities, Community, CommunityMembers, CommunityPosts, CouponCode, UploadCoupons, Subscriptions, \
    UploadTeams, ImageAnalysisDB, VoiceCommands, KeyManagement, RestrictedKeywords, FreeSubscriptions, CapturedImages, \
    BankAccounts, Purchases, FeedComments, FeedLikes, Chatbots, WhatsappConfiguration, ChatBotHistory, \
    WhatsappAccountRequest, WechatMessages, InternalExceptions, WeChatOfficialConfiguration, RoomLoginRequests, \
    GeneralRoomLoginRequests, VoiceCommandsHistory


# Register your models here.


class VoiceToVoiceRequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'requests_send', 'added_on', 'updated_on')
    list_filter = ('added_on', 'user__premium',)


class CommunityMembersAdmin(admin.ModelAdmin):
    list_display = ("user", "community", "added_on")


class UploadCouponsAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        file = form.cleaned_data.get('file')
        if file:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                raise ValueError('Invalid file format')
            records = df.to_dict(orient='records')
            for coupon in records:
                try:
                    provider = coupon["coupon_provider"]
                    coupon_code = coupon["coupon_code"]
                    currency = coupon["currency"]
                    coupon_price = coupon["coupon_price"]
                    start_date = coupon["start_date"]
                    expiry_date = coupon["expiry_date"]
                    CouponCode.objects.create(
                        provider=provider, currency=currency, code=coupon_code,
                        price=coupon_price, start_date=start_date, end_date=expiry_date)
                except KeyError:
                    raise ValueError('Invalid file format')
                except Exception as e:
                    raise ValueError(str(e))
        super().save_model(request, obj, form, change)


class UploadTeamsAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        file = form.cleaned_data.get('file')
        if file:
            # Create a file-like object from the uploaded content
            file_content = file.read()
            file.seek(0)  # Reset file pointer to the beginning

            # Detect the encoding of the file content
            result = chardet.detect(file_content)
            encoding = result['encoding']

            if file.name.endswith('.csv'):
                # Use StringIO to create a file-like object for pandas
                file_io = io.StringIO(file_content.decode(encoding))
                df = pd.read_csv(file_io)
            elif file.name.endswith('.xlsx'):
                # For Excel files, you can directly use pd.read_excel
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                raise ValueError('Invalid file format')

            records = df.to_dict(orient='records')
            for coupon in records:
                try:
                    name = coupon["team_name"]
                    print(name, coupon)
                    Community.objects.create(name=name)
                except KeyError:
                    raise ValueError('Invalid file format')
                except Exception as e:
                    raise ValueError(str(e))
        super().save_model(request, obj, form, change)


class CouponCodeAdmin(admin.ModelAdmin):
    list_display = ('provider', 'currency', 'code', 'is_expired', 'price', 'start_date', 'end_date', 'added_on')


class CommunityPostsAdmin(admin.ModelAdmin):
    list_display = ("user", "item", "community", "added_on")


class CommunityAdmin(admin.ModelAdmin):
    list_display = ("community_id", "priority", "latitude", "longitude",  "name", "leader", "added_on")
    search_fields = ("name", "community_id", "leader__email")


class PurchasesAdmin(admin.ModelAdmin):
    list_display = ("item", "user", "buyer_email", "is_paid", "is_shipped", "quantity", "updated_on")


class FeedCommentsAdmin(admin.ModelAdmin):
    list_display = ("user", "comment_id", "post", "comment", "parent", "added_on")
    list_filter = ("added_on", )
    search_fields = ("user__email", )


class FeedLikesAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "added_on")
    search_fields = ("user__email", )


class ChatbotsAdmin(admin.ModelAdmin):
    list_display = ("user", "chatbot_id", "title", "created_on", "updated_at")
    search_fields = ("user__email",)


class ChatBotHistoryAdmin(admin.ModelAdmin):
    list_display = ("chatbot", "user", "query", "added_on")


class WhatsappAccountRequestAdmin(admin.ModelAdmin):
    list_display = ("phone_no", "account_created", "added_on")


class ItemsAdmin(admin.ModelAdmin):
    list_display = ("item_id", "title", "listing", "category", "price", "added_on")
    list_filter = ("listing", "added_on")


class WechatMessagesAdmin(admin.ModelAdmin):
    list_display = ('wechat_id', 'msg_type', 'event_type', 'added_on')
    list_filter = ("added_on",)


class WeChatOfficialConfigurationAdmin(admin.ModelAdmin):
    list_display = ('official_id', 'app_id', 'secret_id', 'added_on')


class RoomLoginRequestsAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "is_expired", "added_on")
    list_filter = ("is_expired", "added_on")


class GeneralRoomLoginRequestsAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "is_expired", "added_on")
    list_filter = ("is_expired", "added_on")


class VoiceCommandsAdmin(admin.ModelAdmin):
    list_display = ("input", "switch", "added_on", "updated_on")


admin.site.register(Category)
admin.site.register(Items, ItemsAdmin)
admin.site.register(ResponsesDB)
admin.site.register(ImagesDB)
admin.site.register(ShopAccess)
admin.site.register(Plans)
admin.site.register(Industries)
admin.site.register(Jobs)
admin.site.register(VoiceCommandsHistory)
admin.site.register(Capabilities)
admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityPosts, CommunityPostsAdmin)
admin.site.register(CouponCode, CouponCodeAdmin)
admin.site.register(UploadCoupons, UploadCouponsAdmin)
admin.site.register(UploadTeams, UploadTeamsAdmin)
admin.site.register(Subscriptions)
admin.site.register(FreeSubscriptions)
admin.site.register(VoiceToVoiceRequests, VoiceToVoiceRequestsAdmin)
admin.site.register(CommunityMembers, CommunityMembersAdmin)
admin.site.register(ImageAnalysisDB)
admin.site.register(VoiceCommands, VoiceCommandsAdmin)
admin.site.register(KeyManagement)
admin.site.register(RestrictedKeywords)
admin.site.register(CapturedImages)
admin.site.register(BankAccounts)
admin.site.register(Purchases, PurchasesAdmin)
admin.site.register(FeedComments, FeedCommentsAdmin)
admin.site.register(FeedLikes, FeedLikesAdmin)
admin.site.register(Chatbots, ChatbotsAdmin)
admin.site.register(WhatsappConfiguration)
admin.site.register(WechatMessages, WechatMessagesAdmin)
admin.site.register(InternalExceptions)
admin.site.register(ChatBotHistory, ChatBotHistoryAdmin)
admin.site.register(WhatsappAccountRequest, WhatsappAccountRequestAdmin)
admin.site.register(WeChatOfficialConfiguration, WeChatOfficialConfigurationAdmin)
admin.site.register(RoomLoginRequests, RoomLoginRequestsAdmin)
admin.site.register(GeneralRoomLoginRequests, GeneralRoomLoginRequestsAdmin)


