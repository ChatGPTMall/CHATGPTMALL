from django.contrib import admin
from engine.models import Items, Category, ResponsesDB, VoiceToVoiceRequests, ImagesDB, ShopAccess
# Register your models here.


class VoiceToVoiceRequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'requests_send', 'added_on', 'updated_on')
    list_filter = ('added_on', 'user__premium',)


admin.site.register(Category)
admin.site.register(Items)
admin.site.register(ResponsesDB)
admin.site.register(ImagesDB)
admin.site.register(ShopAccess)
admin.site.register(VoiceToVoiceRequests, VoiceToVoiceRequestsAdmin)
