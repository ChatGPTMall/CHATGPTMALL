import pandas as pd
from django.contrib import admin
from engine.models import Items, Category, ResponsesDB, VoiceToVoiceRequests, ImagesDB, ShopAccess, Plans, Industries, \
    Jobs, Capabilities, Community, CommunityMembers, CommunityPosts, CouponCode, UploadCoupons, Subscriptions


# Register your models here.


class VoiceToVoiceRequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'requests_send', 'added_on', 'updated_on')
    list_filter = ('added_on', 'user__premium',)


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


class CouponCodeAdmin(admin.ModelAdmin):
    list_display = ('provider', 'currency', 'code', 'is_expired', 'price', 'start_date', 'end_date', 'added_on')


admin.site.register(Category)
admin.site.register(Items)
admin.site.register(ResponsesDB)
admin.site.register(ImagesDB)
admin.site.register(ShopAccess)
admin.site.register(Plans)
admin.site.register(Industries)
admin.site.register(Jobs)
admin.site.register(Capabilities)
admin.site.register(Community)
admin.site.register(CommunityMembers)
admin.site.register(CommunityPosts)
admin.site.register(CouponCode, CouponCodeAdmin)
admin.site.register(UploadCoupons, UploadCouponsAdmin)
admin.site.register(Subscriptions)
admin.site.register(VoiceToVoiceRequests, VoiceToVoiceRequestsAdmin)
