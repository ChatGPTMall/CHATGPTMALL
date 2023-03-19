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
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from engine.views import TextToTexTView
from users.views import HomepageView, LoginView, RegisterView, VoiceToImage, UploadVoice, VoiceOutPut, VoiceToVoice, \
    get_chatgpt_response, TextToText, Logout, ShopVoiceToVoice, ApiKeyView, CreateAPIkey, DeleteAPIkey, OurPlans, \
    IndustriesView, GetIndustriesData, TextToImage, GetImages

admin.site.site_header = 'CHATGPTMALL'  # default: "Django Administration"
admin.site.index_title = 'CHATGPTMALL Admin Area'  # default: "Site administration"
admin.site.site_title = 'CHATGPTMALL Admin'  # default: "Django site admin"

schema_view = get_schema_view(
    openapi.Info(
        title="CHATGPTMALL APIs Documentation",
        default_version='v1',
        description="Document to try out all APIs for CHATGPTMALL",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="faisalbashir353@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('docs/', schema_view),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^docs/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
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
    path('api/text_to_image/', TextToImage, name="TextToImage"),
    path('api/images/', GetImages, name="GetImages"),

    path("create/api_key/", CreateAPIkey, name="CreateAPIkey"),
    path("delete_key/", DeleteAPIkey, name="DeleteAPIkey"),
    path('api/keys/', ApiKeyView, name="ApiKeyView"),

    path('plans/', OurPlans, name="our_plans"),
    path("ajax/industries/", GetIndustriesData, name="GetIndustriesData"),
    path('marketing/industries/', IndustriesView, name="IndustriesView"),

    # API's
    path('api/v1/text_to_text/', TextToTexTView.as_view(), name="TextToTexTView"),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
