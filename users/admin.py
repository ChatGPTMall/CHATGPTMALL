from django.contrib import admin
from users.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        ('User Info', {'fields': ('email', 'password', 'first_name', 'last_name', 'premium')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        ('Important dates', {'fields': ('joined_on',)})
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

    list_display = ('email', 'first_name', 'last_name', 'joined_on')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'joined_on')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('joined_on',)


admin.site.register(User, UserAdmin)
