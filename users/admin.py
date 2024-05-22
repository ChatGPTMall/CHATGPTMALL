import pandas as pd
from django.contrib import admin
from users.models import User, UploadUsers, ChinaUsers, WechatOfficialAccount
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        ('User Info', {'fields': ('email', 'password', 'first_name', 'last_name', 'phone_no', 'premium',
                                  'access', 'credits', 'room', 'wechat_ids')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        ('Important dates', {'fields': ('joined_on', 'purchased_on')})
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2',)
            }
        ),
    )

    list_display = ('email', 'first_name', 'last_name', 'phone_no', 'wechat_ids', 'access',
                    'purchased_on', 'joined_on')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'joined_on', 'access')
    search_fields = ('email', 'phone_no')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('joined_on',)


class UploadUsersAdmin(admin.ModelAdmin):

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
                    last_name = coupon["last_name"]
                    first_name = coupon["first_name"]
                    email = coupon["email"]
                    password = coupon["password"]
                    user = User.objects.create(last_name=last_name, first_name=first_name, email=email)
                    user.set_password(password)
                    user.save()
                except KeyError:
                    raise ValueError('Invalid file format')
                except Exception as e:
                    raise ValueError(str(e))
        super().save_model(request, obj, form, change)


class ChinaUsersAdmin(admin.ModelAdmin):
    list_display = ("user_id", "wechat_id", "joined_on")


class WechatOfficialAccountAdmin(admin.ModelAdmin):
    list_display = ("user_id", "official_id", "joined_on")


admin.site.register(User, UserAdmin)
admin.site.register(ChinaUsers, ChinaUsersAdmin)
admin.site.register(WechatOfficialAccount, WechatOfficialAccountAdmin)
admin.site.register(UploadUsers, UploadUsersAdmin)
