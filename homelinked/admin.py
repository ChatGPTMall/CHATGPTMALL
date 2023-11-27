from django.contrib import admin

from homelinked.models import HomePlans, HomePlanPurchases, HomepageNewFeature, CreditsHistory


class HomepageNewFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "color", "added_on", "updated_on")


class CreditsHistoryAdmin(admin.ModelAdmin):
    list_display = ("credit_id", "user", "feature", "tokens", "added_on")


# Register your models here.
admin.site.register(HomePlans)
admin.site.register(HomePlanPurchases)
admin.site.register(HomepageNewFeature, HomepageNewFeatureAdmin)
admin.site.register(CreditsHistory, CreditsHistoryAdmin)
