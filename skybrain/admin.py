from django.contrib import admin
from skybrain.models import Organization, LicensesRequests, Room, RoomHistory, RoomItems


class RoomHistoryAdmin(admin.ModelAdmin):
    list_display = ("room", "user_input", "added_on")


admin.site.register(Organization)
admin.site.register(LicensesRequests)
admin.site.register(Room)
admin.site.register(RoomItems)
admin.site.register(RoomHistory, RoomHistoryAdmin)
