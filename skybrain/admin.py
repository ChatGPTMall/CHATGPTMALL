from django.contrib import admin
from skybrain.models import Organization, LicensesRequests, Room, RoomHistory


class RoomHistoryAdmin(admin.ModelAdmin):
    list_display = ("room", "user_input", "added_on")


admin.site.register(Organization)
admin.site.register(LicensesRequests)
admin.site.register(Room)
admin.site.register(RoomHistory, RoomHistoryAdmin)
