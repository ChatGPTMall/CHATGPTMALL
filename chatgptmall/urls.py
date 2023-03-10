"""chatgptmall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from users.views import HomepageView, LoginView, RegisterView, VoiceToImage, UploadVoice, VoiceOutPut, VoiceToVoice, \
    get_chatgpt_response, TextToText, Logout, ShopVoiceToVoice

admin.site.site_header = 'CHATGPTMALL'  # default: "Django Administration"
admin.site.index_title = 'CHATGPTMALL Admin Area'  # default: "Site administration"
admin.site.site_title = 'CHATGPTMALL Admin'  # default: "Django site admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomepageView, name="HomepageView"),
    path('api/login/', LoginView, name="LoginView"),
    path('api/logout', Logout, name="Logout"),
    path('api/register/', RegisterView, name="RegisterView"),
    path('api/convert/voice_to_image/', VoiceToImage, name="VoiceToImage"),
    path('shop/', ShopVoiceToVoice, name="ShopVoiceToVoice"),

    path('api/show_voice_out_put/', VoiceOutPut, name="VoiceOutPut"),
    path('upload_voice/', UploadVoice, name="UploadVoice"),

    path('api/voice_to_voice/', VoiceToVoice, name="VoiceToVoice"),
    path('api/get_voice/', get_chatgpt_response, name="get_chatgpt_response"),

    path('api/text_to_text/', TextToText, name="TextToText"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
