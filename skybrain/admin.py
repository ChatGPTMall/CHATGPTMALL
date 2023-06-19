from django.contrib import admin
from skybrain.models import Organization, LicensesRequests, Room, RoomHistory, RoomItems, CustomerSupport


class RoomHistoryAdmin(admin.ModelAdmin):
    list_display = ("room", "user_input", "added_on")


class RoomItemsAdmin(admin.ModelAdmin):
    list_display = ("room", "name", "price", "category", "is_private", "added_on")
    list_filter = ("room__organization", )


class CustomerSupportAdmin(admin.ModelAdmin):
    list_display = ("room", "user_input", "has_replied", "added_on")


admin.site.register(Organization)
admin.site.register(LicensesRequests)
admin.site.register(Room)
admin.site.register(CustomerSupport, CustomerSupportAdmin)
admin.site.register(RoomItems, RoomItemsAdmin)
admin.site.register(RoomHistory, RoomHistoryAdmin)
