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
from engine.views import TextToTexTView, CreateCheckoutSessionView, TextToImageView, ImageAnalysisView, \
    ObjectsDetectionView, ShopItemsView, ShopCategoriesView, GetItemsView
from users.views import HomepageView, LoginView, RegisterView, VoiceToImage, UploadVoice, VoiceOutPut, VoiceToVoice, \
    get_chatgpt_response, TextToText, Logout, ShopVoiceToVoice, ApiKeyView, CreateAPIkey, DeleteAPIkey, OurPlans, \
    IndustriesView, GetIndustriesData, TextToImage, GetImages, JobsView, CapabilitiesView, Communities, JoinCommunity, \
    SendPostCommunity, Checkout, PaymentSuccess, PaymentCancel, ValidateCouponCode, JoinedCommunities, ProfileView, \
    ProfileUpdate, ShareTeam, DownloadTeams, ShopWithText, ItemHowToUse, CreateTeams, ImageToImage, ImageAnalysis, \
    SaveAnalysisImage, ObjectsDetection, ObjDetect, SendObjectCommunity, VideoAnalysis, AnalysisVideo, \
    UploadCommunityPost, LearHowToUse, GetCommand, ResponseCommand, ImageToImageCalculate, \
    KeyManagementView, ForgotPassword, ChangePassword, RenewSubscription, deletekey, TextToVoice, \
    MicrosoftKeyManagementView

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
    path('api/profile/', ProfileView, name="ProfileView"),
    path('api/update/profile/', ProfileUpdate, name="ProfileUpdate"),
    path('api/convert/voice_to_image/', VoiceToImage, name="VoiceToImage"),
    path('shop/', ShopVoiceToVoice, name="ShopVoiceToVoice"),
    path('api/text_to_voice/', TextToVoice, name="TextToVoice"),
    path('api/show_voice_out_put/', VoiceOutPut, name="VoiceOutPut"),
    path('upload_voice/', UploadVoice, name="UploadVoice"),
    path('voice/command/', GetCommand, name="GetCommand"),
    path('response/commands/', ResponseCommand, name="ResponseCommand"),

    path('api/voice_to_voice/', VoiceToVoice, name="VoiceToVoice"),
    path('api/get_voice/', get_chatgpt_response, name="get_chatgpt_response"),

    path('api/text_to_text/', TextToText, name="TextToText"),
    path('api/text_to_image/', TextToImage, name="TextToImage"),
    path('api/image_to_image/', ImageToImage, name="ImageToImage"),
    path('api/image_to_image/calculate/', ImageToImageCalculate, name="ImageToImageCalculate"),
    path('api/image/analysis/', ImageAnalysis, name="ImageAnalysis"),
    path('api/v1/video/analysis/', VideoAnalysis, name="VideoAnalysis"),
    path('api/image/objects/detection/', ObjectsDetection, name="ObjectsDetection"),
    path('api/images/', GetImages, name="GetImages"),
    path("analysis/image/save/", SaveAnalysisImage, name="SaveAnalysisImage"),
    path("analysis/video/", AnalysisVideo, name="AnalysisVideo"),
    path("objects/detect/", ObjDetect, name="ObjDetect"),

    path("create/api_key/", CreateAPIkey, name="CreateAPIkey"),
    path("delete_key/", DeleteAPIkey, name="DeleteAPIkey"),
    path('api/keys/', ApiKeyView, name="ApiKeyView"),

    path('plans/', OurPlans, name="our_plans"),
    path("ajax/industries/", GetIndustriesData, name="GetIndustriesData"),
    path('marketing/industries/', IndustriesView, name="IndustriesView"),
    path('marketing/jobs/', JobsView, name="JobsView"),
    path('marketing/capabilities/', CapabilitiesView, name="CapabilitiesView"),

    path("communities/", Communities, name="Communities"),
    path("create/communities/", CreateTeams, name="CreateTeams"),
    path("joined/communities/", JoinedCommunities, name="JoinedCommunities"),
    path("join/community/", JoinCommunity, name="JoinCommunity"),
    path("send/post/community/", SendPostCommunity, name="SendPostCommunity"),
    path("send/object/community/", SendObjectCommunity, name="SendObjectCommunity"),
    path("upload/community/post/", UploadCommunityPost, name="UploadCommunityPost"),

    path("checkout/<int:plan_id>/", Checkout, name="Checkout"),
    path("checkout/Session/", CreateCheckoutSessionView, name="CreateCheckoutSessionView"),
    path("payment/success/<int:plan_id>/<int:user_id>/", PaymentSuccess, name="payment-success"),
    path("payment/cancel/", PaymentCancel, name="payment-cancel"),
    path("validate/coupon_code/<str:coupon_code>/", ValidateCouponCode, name="ValidateCouponCode"),

    # Shop
    path("api/v1/shop/text/", ShopWithText, name="ShopWithText"),
    path("item/how_to_use/<int:item_id>/", ItemHowToUse, name="ItemHowToUse"),
    path("item/details/<int:item_id>/", LearHowToUse, name="LearHowToUse"),

    # API's
    path('api/v1/text_to_text/', TextToTexTView.as_view(), name="TextToTexTView"),
    path('api/v1/text_to_image/', TextToImageView.as_view(), name="TextToImagesAPI"),
    path('api/v1/image/analysis/', ImageAnalysisView.as_view(), name="ImageAnalysisView"),
    path('api/v1/objects/detection/', ObjectsDetectionView.as_view(), name="ObjectsDetectionView"),
    path('api/v1/shop/items/', ShopItemsView.as_view(), name="ShopItemsView"),
    path('api/v1/items/', GetItemsView.as_view(), name="ShGetItemsViewopItemsView"),
    path('api/v1/shop/categories/', ShopCategoriesView.as_view(), name="ShopItemsView"),

    path("team/share/<int:team_id>/", ShareTeam, name="ShareTeam"),
    path("downloads/teams/", DownloadTeams, name="DownloadTeams"),

    path("api/key/management/", KeyManagementView, name="KeyManagement"),
    path("api/microsoft/keys/", MicrosoftKeyManagementView, name="MicrosoftKeyManagementView"),
    path("api/forgot/password/", ForgotPassword, name="ForgotPassword"),
    path("api/change/password/", ChangePassword, name="ChangePassword"),

    path("api/renew/subscription/", RenewSubscription, name="RenewSubscription"),

    path("delete/key/<int:id>/", deletekey, name="deletekey"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
