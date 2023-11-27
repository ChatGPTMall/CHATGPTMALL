import pandas as pd
from django.contrib import admin
from users.models import User, UploadUsers
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        ('User Info', {'fields': ('email', 'password', 'first_name', 'last_name', 'premium', 'access', 'credits', 'room')}),
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

    list_display = ('email', 'first_name', 'last_name', 'access', 'purchased_on', 'joined_on')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'joined_on', 'access')
    search_fields = ('email',)
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


admin.site.register(User, UserAdmin)
admin.site.register(UploadUsers, UploadUsersAdmin)
