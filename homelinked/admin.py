from django.contrib import admin

from homelinked.models import HomePlans, HomePlanPurchases, HomepageNewFeature

class HomepageNewFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "color", "added_on", "updated_on")

# Register your models here.
admin.site.register(HomePlans)
admin.site.register(HomePlanPurchases)
admin.site.register(HomepageNewFeature, HomepageNewFeatureAdmin)
