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
    ObjectsDetectionView, ShopItemsView, ShopCategoriesView, GetItemsView, TextToTexTOpeniaiView, \
    TextToTexTMicrosoftView, TranscribeAudio, RoomTextToTexTView, ItemCreateCheckoutSessionView
from homelinked.views import HomePlansAPIView, HomepageNewFeatureView, CommunitiesView
from skybrain.views import LicensesView, CreateLicensesView, OrganizationRooms, SkybrainCustomerRoom, ValidateRoom, \
    HistoryRoom, ItemsRoomView, UploadItemsRoomView, PublicItemsRoomView, Organizationsview, CSQueriesView, \
    CSQueriesUpdateView, FavouritesView, ItemsSendEmailView, UnsubscribeView, CreateRooms, CreateOrganizations, \
    ItemsRoomDetailView, ShareRoomItems, RoomHistoryDetailView, ShareRoomResponse, OCRImageUploadView, UpdateRoomView, \
    CustomInstructionsView, GenerateImageView, RoomAccessShare, URLOCRImageUploadView
from users.views import HomepageView, LoginView, RegisterView, VoiceToImage, UploadVoice, VoiceOutPut, VoiceToVoice, \
    get_chatgpt_response, TextToText, Logout, ShopVoiceToVoice, ApiKeyView, CreateAPIkey, DeleteAPIkey, OurPlans, \
    IndustriesView, GetIndustriesData, TextToImage, GetImages, JobsView, CapabilitiesView, Communities, JoinCommunity, \
    SendPostCommunity, Checkout, PaymentSuccess, PaymentCancel, ValidateCouponCode, JoinedCommunities, ProfileView, \
    ProfileUpdate, ShareTeam, DownloadTeams, ShopWithText, ItemHowToUse, CreateTeams, ImageToImage, ImageAnalysis, \
    SaveAnalysisImage, ObjectsDetection, ObjDetect, SendObjectCommunity, VideoAnalysis, AnalysisVideo, \
    UploadCommunityPost, LearHowToUse, GetCommand, ResponseCommand, ImageToImageCalculate, \
    KeyManagementView, ForgotPassword, ChangePassword, RenewSubscription, deletekey, TextToVoice, \
    MicrosoftKeyManagementView, get_text, WatchVideo, get_image, TextToCommand, AiModels, VoiceToVoiceDetail, \
    VoiceToImageDetail, TextToVoiceDetail, TextToTextDetail, TextToImageDetail, ImageToImageDetail, ImageAnalysisDetail, \
    ImageDetectDetail, VoiceToCommandDetail, TextToCommandDetail, ImageToTextDetail, ImageToText, GetOcrImage, \
    OCRContentGenerate, SaveCapturedPhoto, ImageAnalysisOCR, voice2voicePlanDetail, RedirectPlan, voice2ImagePlanDetail, \
    text2VoicePlanDetail, text2TextPlanDetail, text2ImagePlanDetail, image2ImagePlanDetail, \
    object_detectPlanDetail, voice2commandPlanDetail, text2commandPlanDetail, OcrPlanDetail, imageAnalysisPlanDetail, \
    RetailBotsView, ShopCheckout, ItemPaymentSuccess, RegisterViewV2, LoginViewV2, ProfileViewV2, GetUserItemData

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
    path('ai/models/', AiModels, name="AiModels"),
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
    path('text/command/', TextToCommand, name="TextToCommand"),
    path('response/commands/', ResponseCommand, name="ResponseCommand"),

    path('api/voice_to_voice/', VoiceToVoice, name="VoiceToVoice"),
    path('api/get_voice/', get_chatgpt_response, name="get_chatgpt_response"),
    path('api/get_text/', get_text, name="get_text"),
    path('api/get_image/', get_image, name="get_image"),

    path('api/text_to_text/', TextToText, name="TextToText"),
    path('api/text_to_image/', TextToImage, name="TextToImage"),
    path('api/image_to_image/', ImageToImage, name="ImageToImage"),
    path('api/image_to_text/', ImageToText, name="ImageToText"),
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
    path("shop/item/checkout/<uuid:item_id>/", ShopCheckout, name="ShopCheckout"),
    path("item/user/info/<uuid:item_id>/", GetUserItemData, name="GetUserItemData"),
    path("item/how_to_use/<int:item_id>/", ItemHowToUse, name="ItemHowToUse"),
    path("item/details/<uuid:item_id>/", LearHowToUse, name="LearHowToUse"),
    path("item/checkout/Session/", ItemCreateCheckoutSessionView, name="ItemCreateCheckoutSessionView"),
    path("item/payment/success/<uuid:item_id>/<uuid:user_id>/", ItemPaymentSuccess, name="item-payment-success"),

    # API's
    path('api/v1/vision/', TextToTexTView.as_view(), name="TextToTexTView"),
    path('api/v1/openai/text_to_text/', TextToTexTOpeniaiView.as_view(), name="TextToTexTOpeniaiView"),
    path('api/v1/text_to_image/', TextToImageView.as_view(), name="TextToImagesAPI"),

    path('api/v1/room/text_to_text/', RoomTextToTexTView.as_view(), name="RoomTextToTexTView"),
    path('api/v1/ms/text_to_text/', TextToTexTMicrosoftView.as_view(), name="chatgptmalldb"),
    path('api/v1/transcribe/audio/', TranscribeAudio.as_view(), name="TranscribeAudio"),
    path('api/v1/image/analysis/', ImageAnalysisView.as_view(), name="ImageAnalysisView"),
    path('api/v1/objects/detection/', ObjectsDetectionView.as_view(), name="ObjectsDetectionView"),
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
    path("watch/video/<uuid:item_id>/", WatchVideo, name="WatchVideo"),

    path("models/text_to_text/detail/", TextToTextDetail, name="TextToTextDetail"),
    path("models/voice_to_voice/detail/", VoiceToVoiceDetail, name="VoiceToVoiceDetail"),
    path("models/voice_to_image/detail/", VoiceToImageDetail, name="VoiceToImageDetail"),
    path("models/Text_to_voice/detail/", TextToVoiceDetail, name="TextToVoiceDetail"),
    path("models/text_to_image/detail/", TextToImageDetail, name="TextToImageDetail"),
    path("models/image_to_image/detail/", ImageToImageDetail, name="ImageToImageDetail"),
    path("models/text_analysis/detail/", ImageAnalysisDetail, name="ImageAnalysisDetail"),
    path("models/image_detect/detail/", ImageDetectDetail, name="ImageDetectDetail"),
    path("models/voice_to_command/detail/", VoiceToCommandDetail, name="VoiceToCommandDetail"),
    path("models/text_to_command/detail/", TextToCommandDetail, name="TextToCommandDetail"),
    path("models/image_to_text/detail/", ImageToTextDetail, name="ImageToTextDetail"),

    # OCR
    path("json/ocr/image/", GetOcrImage, name="GetOcrImage"),
    path("ocr/content/generate/", OCRContentGenerate, name="OCRContentGenerate"),

    # capture video
    path("capture/save_photo/", SaveCapturedPhoto, name="SaveCapturedPhoto"),
    path("analysis/ocr/image/", ImageAnalysisOCR, name="ImageAnalysisOCR"),

    # plan details
    path("redirect/plan/<int:plan_id>/", RedirectPlan, name="RedirectPlan"),
    path("voice2voice/plan/detail/", voice2voicePlanDetail, name="voice2voicePlanDetail"),
    path("voice2image/plan/detail/", voice2ImagePlanDetail, name="voice2ImagePlanDetail"),
    path("text2voice/plan/detail/", text2VoicePlanDetail, name="text2VoicePlanDetail"),
    path("text2text/plan/detail/", text2TextPlanDetail, name="text2TextPlanDetail"),
    path("text2image/plan/detail/", text2ImagePlanDetail, name="text2ImagePlanDetail"),
    path("image2image/plan/detail/", image2ImagePlanDetail, name="image2ImagePlanDetail"),
    path("image_analysis/plan/detail/", imageAnalysisPlanDetail, name="imageAnalysisPlanDetail"),
    path("object_detect/plan/detail/", object_detectPlanDetail, name="object_detectPlanDetail"),
    path("voice2command/plan/detail/", voice2commandPlanDetail, name="voice2commandPlanDetail"),
    path("text2command/plan/detail/", text2commandPlanDetail, name="text2commandPlanDetail"),
    path("ocr/plan/detail/", OcrPlanDetail, name="OcrPlanDetail"),

    # retail
    path("api/retail_bots/", RetailBotsView, name="RetailBotsView"),

    # sky brain APIs
    path("api/v1/licenses/", LicensesView.as_view(), name="LicensesView"),
    path("api/v1/create_licenses/", CreateLicensesView.as_view(), name="CreateLicensesView"),
    path("api/v1/organization/rooms/", OrganizationRooms.as_view(), name="OrganizationRooms"),
    path("api/v1/skybrain/customer/", SkybrainCustomerRoom.as_view(), name="SkybrainCustomerRoom"),
    path("api/v1/room/validate/", ValidateRoom.as_view(), name="ValidateRoom"),
    path("api/v1/room/history/", HistoryRoom.as_view(), name="HistoryRoom"),
    path("api/v1/room/items/", ItemsRoomView.as_view(), name="ItemsRoomView"),
    path("api/v1/room/items/detail/", ItemsRoomDetailView.as_view(), name="ItemsRoomDetailView"),
    path("api/v1/room/history/detail/", RoomHistoryDetailView.as_view(), name="RoomHistoryDetailView"),
    path("api/v1/room/items/public/", PublicItemsRoomView.as_view(), name="PublicItemsRoomView"),
    path("api/v1/room/items/upload/", UploadItemsRoomView.as_view(), name="UploadItemsRoomView"),
    path("api/v1/organizations/", Organizationsview.as_view(), name="Organizationsview"),
    path("api/v1/room/CS/queries/", CSQueriesView.as_view(), name="CSQueriesView"),
    path("api/v1/room/queries/update/", CSQueriesUpdateView.as_view(), name="CSQueriesUpdateView"),
    path("api/v1/favourites/room/", FavouritesView.as_view(), name="FavouritesView"),
    path("api/v1/room/items/email/", ItemsSendEmailView.as_view(), name="ItemsSendEmailView"),
    path("unsubscribe/<str:email>/", UnsubscribeView, name="UnsubscribeView"),
    path("create/organizations/", CreateOrganizations, name="CreateOrganizations"),
    path("create/org/rooms/", CreateRooms, name="CreateRoomsView"),
    path("api/v1/room/items/share/", ShareRoomItems.as_view(), name="ShareRoomItems"),
    path("api/v1/room/response/share/", ShareRoomResponse.as_view(), name="ShareRoomResponse"),
    path("api/v1/room/ocr/", OCRImageUploadView.as_view(), name="OCRImageUploadView"),
    path("api/v1/room/update/", UpdateRoomView.as_view(), name="UpdateRoomView"),
    path("api/v1/room/custom_instructions/", CustomInstructionsView.as_view(), name="CustomInstructionsView"),
    path("api/v1/room/generate/image/", GenerateImageView.as_view(), name="GenerateImageView"),
    path("api/v1/room/share/", RoomAccessShare.as_view(), name="RoomAccessShare"),
    path("api/v1/room/image/url/ocr/", URLOCRImageUploadView.as_view(), name="URLOCRImageUploadView"),

    # v2 authentication APIs
    path("api/v2/register/", RegisterViewV2.as_view(), name="RegisterViewV2"),
    path("api/v2/login/", LoginViewV2.as_view(), name="LoginViewV2"),
    path("api/v2/profile/", ProfileViewV2.as_view(), name="ProfileViewV2"),

    # home APIs v1
    path("api/v1/home/plans/", HomePlansAPIView.as_view(), name="HomePlansAPIView"),
    path("api/v1/home/feature/", HomepageNewFeatureView.as_view(), name="HomepageNewFeatureView"),
    path("api/v1/home/communities/", CommunitiesView.as_view(), name="CommunitiesView"),
    path('api/v1/shop/items/', ShopItemsView.as_view(), name="ShopItemsView"),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
