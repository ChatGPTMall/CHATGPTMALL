from django.contrib import admin

from homelinked.models import HomePlans, HomePlanPurchases, HomepageNewFeature, CreditsHistory, WeChatAccounts, \
    RoomWhatsAppItems, VendingMachine, VendingMachineItem


class HomepageNewFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "color", "added_on", "updated_on")


class CreditsHistoryAdmin(admin.ModelAdmin):
    list_display = ("credit_id", "user", "feature", "tokens", "added_on")


class WeChatAccountsAdmin(admin.ModelAdmin):
    list_display = ("user", "wechat_id", "app_id", "secret", "access_token", "added_on")


class RoomWhatsAppItemsAdmin(admin.ModelAdmin):
    list_display = ("item", "room", "listing", "added_on")


@admin.register(VendingMachine)
class VendingMachineAdmin(admin.ModelAdmin):
    list_display = ("machine_id", "location")
    search_fields = ("machine_id", "location")
    readonly_fields = ("machine_id",)

@admin.register(VendingMachineItem)
class VendingMachineItemAdmin(admin.ModelAdmin):
    list_display = ("vending_machine", "item", "slot_number", "quantity")
    list_filter = ("vending_machine", "item")
    search_fields = ("vending_machine__location", "item__title")


# Register your models here.
admin.site.register(HomePlans)
admin.site.register(HomePlanPurchases)
admin.site.register(HomepageNewFeature, HomepageNewFeatureAdmin)
admin.site.register(CreditsHistory, CreditsHistoryAdmin)
admin.site.register(WeChatAccounts, WeChatAccountsAdmin)
admin.site.register(RoomWhatsAppItems, RoomWhatsAppItemsAdmin)
