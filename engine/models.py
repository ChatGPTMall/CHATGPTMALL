import os
import random
import string
import uuid

from django.db import models
from users.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw, ImageFont
from users.s3_storage import ItemVideosS3Storage


class Category(models.Model):
    title = models.CharField(max_length=200)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Item Categories")

    def __str__(self):
        return self.title


class BankAccounts(models.Model):
    name = models.CharField(_("Bank Name"), unique=True, max_length=100)
    private_key = models.CharField(_("Stripe Private Key"), unique=True, max_length=200)
    public_key = models.CharField(_("Stripe Public Key"), unique=True, max_length=200)
    webhook_key = models.CharField(_("Stripe Webhook Key"), unique=True, max_length=200)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")

    def __str__(self):
        return self.name


class PrivateBankAccounts(models.Model):
    private_key = models.CharField(_("Stripe Private Key"), unique=True, max_length=200)
    public_key = models.CharField(_("Stripe Public Key"), unique=True, max_length=200)
    webhook_key = models.CharField(_("Stripe Webhook Key"), unique=True, max_length=200)
    added_on = models.DateTimeField(auto_now_add=True)


class Items(models.Model):
    item_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="images/items/", null=True, blank=True)
    video = models.FileField(null=True, blank=True, upload_to="items/videos")
    qr_code = models.ImageField(upload_to="images/QR/", null=True, blank=True)
    price = models.FloatField(default=0)
    location = models.CharField(max_length=200, null=True, blank=True)
    stock = models.IntegerField(default=1)
    public_bank = models.ForeignKey(BankAccounts, related_name="public_bank_accounts",
                                    null=True, blank=True, on_delete=models.PROTECT)
    private_bank = models.ForeignKey(PrivateBankAccounts, related_name="private_bank_accounts",
                                     null=True, blank=True, on_delete=models.PROTECT)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        qr_image = qrcode.QRCode(version=1, box_size=10, border=5)
        DEPLOYED_HOST = os.getenv("DEPLOYED_HOST_CHAT", None)
        url = "https://chatgptmall.tech" + "/item/details/{}".format(self.item_id)
        qr_image.add_data(url)

        qr_image.make(fit=True)
        img = qr_image.make_image(fill='black', back_color='white')
        # qr_offset = Image.new('RGB', (310, 310), 'white')
        file_name = f'{self.title}-{self.id}qr.png'
        stream = BytesIO()
        img.save(stream, 'PNG')
        self.qr_code.save(file_name, File(stream), save=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")


class ResponsesDB(models.Model):
    question = models.TextField(_("Users Query"))
    answer = models.TextField(_("Openai Response"))
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = _("Response")
        verbose_name_plural = _("Openai Responses")


class VoiceToVoiceRequests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voice_requests")
    requests_send = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = _("Voice Request")
        verbose_name_plural = _("Voice Requests")


class ImagesDB(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="images", null=True, blank=True)
    question = models.TextField(_("Users Query"))
    images = models.JSONField(default=list, null=True, blank=True)
    image1 = models.ImageField(_("Image One"), upload_to="openai/images", null=True, blank=True)
    image2 = models.ImageField(_("Image Two"), upload_to="openai/images", null=True, blank=True)
    image3 = models.ImageField(_("Image Three"), upload_to="openai/images", null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Openai Images")


class ShopAccess(models.Model):
    switch = models.BooleanField(default=False)

    def __str__(self):
        return str(self.switch)

    class Meta:
        verbose_name = _("ShopAccess")
        verbose_name_plural = _("ShopAccess")


class PlanType(models.TextChoices):
    MONTHLY = "MONTHLY", _('Monthly')
    YEARLY = "YEARLY", _('Yearly')
    TIMEPERIOD = "TIMEPERIOD", _('Time Period')


class AccessTypes(models.TextChoices):
    NO_ACCESS = "NO_ACCESS", _('No Access')
    TEXT_TO_TEXT = "TEXT_TO_TEXT", _('Text To Text')
    TEXT_TO_VOICE = "TEXT_TO_VOICE", _('Text To Voice')
    VOICE_TO_Voice = "VOICE_TO_Voice", _('Voice To Voice')
    VOICE_TO_IMAGE = "VOICE_TO_IMAGE", _('Voice To Image')
    TEXT_TO_IMAGE = "TEXT_TO_IMAGE", _('Text To Image')
    Image_To_Text = "Image_To_Text", _('Image To Text')
    IMAGE_TO_IMAGE = "IMAGE_TO_IMAGE", _('Image To Image')
    IMAGE_ANALYSIS = "IMAGE_ANALYSIS", _('Image Analysis')
    OBJECTS_DETECTION = "OBJECTS_DETECTION", _('Objects Detection')
    VOICE_TO_COMMAND = "VOICE_TO_COMMAND", _('Voice To Command')
    TEXT_TO_COMMAND = "TEXT_TO_COMMAND", _('Text To Command')


class Plans(models.Model):
    title = models.CharField(max_length=200)
    price = models.FloatField(default=0)
    plan_type = models.CharField(choices=PlanType.choices, max_length=30, default="MONTHLY")
    access = models.CharField(choices=AccessTypes.choices, max_length=30, default="NO_ACCESS")
    description = models.TextField()
    days = models.IntegerField(default=5)
    free_requests = models.IntegerField(default=10)
    requests = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Subscription Plan")
        verbose_name_plural = _("Chatgptmall Plans")


class Industries(models.Model):
    title = models.TextField(_("Title"), unique=True)
    slogan = models.TextField(_("Industry Slogan"))
    image = models.ImageField(upload_to="marketing/industries", null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Industry")
        verbose_name_plural = _("Industries")


class Jobs(models.Model):
    title = models.TextField(_("Job Title"), unique=True)
    slogan = models.TextField(_("Job Slogan"))
    image = models.ImageField(upload_to="marketing/jobs", null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("JOb")
        verbose_name_plural = _("Jobs")


class Capabilities(models.Model):
    title = models.TextField(_("Capability Title"), unique=True)
    slogan = models.TextField(_("Capability Slogan"))
    image = models.ImageField(upload_to="marketing/Capabilities", null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Capability")
        verbose_name_plural = _("Capabilities")


def is_aphanum(value):
    """
    check if given value is alphanumeric or not
    :param value:
    :return:
    """
    if not str(value).isalnum():
        raise ValidationError(
            _('%(value)s is not an alpha numeric value'),
            params={'value': value},
        )


def create_alphanum():
    """
    Create a random alphanum
    as default
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Community(models.Model):
    community_id = models.CharField(unique=True, null=True, default=create_alphanum, max_length=6,
                                    validators=[MinLengthValidator(6), is_aphanum])
    name = models.CharField(_("Community Name"), max_length=150)
    logo = models.ImageField(upload_to="Communities/Logo", null=True, blank=True)
    leader = models.ForeignKey(User, related_name='community_leaders',
                               on_delete=models.CASCADE, default=1, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_members(self):
        return CommunityMembers.objects.filter(community__community_id=self.community_id).count()

    class Meta:
        verbose_name = _("Community")
        verbose_name_plural = _("Communities")


class CommunityMembers(models.Model):
    community = models.ForeignKey(Community, related_name="members", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='team', on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Community Members")


class CommunityPosts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    community = models.ForeignKey(Community, related_name="feed", on_delete=models.CASCADE)
    is_object = models.BooleanField(default=False)
    question = models.TextField(_("User Question"), null=True, blank=True)
    response = models.TextField(_("AI Response"), null=True, blank=True)
    input_image = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="community/images", null=True, blank=True)
    response_image = models.URLField(null=True, blank=True)
    qrcode = models.ImageField(upload_to="community/qr_code", null=True, blank=True)
    video = models.FileField(upload_to="community/video", null=True, blank=True)
    image1 = models.TextField(null=True, blank=True)
    image2 = models.TextField(null=True, blank=True)
    image3 = models.TextField(null=True, blank=True)
    item = models.ForeignKey(Items, related_name="com_posts", on_delete=models.CASCADE, null=True, blank=True)
    item_name = models.CharField(max_length=100, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = _("Community Post")
        verbose_name_plural = _("Community Posts")


class CouponCode(models.Model):
    provider = models.CharField(_("Coupon Provider"), default="CHATGPTMALL", max_length=200)
    currency = models.CharField(max_length=100)
    code = models.CharField(_("Coupon Code"), max_length=35)
    price = models.FloatField(_("Coupon Discount"), default=0)
    is_expired = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _("Coupon Code")
        verbose_name_plural = _("Coupons")


class Subscriptions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")
    plan = models.ForeignKey(Plans, models.CASCADE, related_name="plan_purchases")
    is_expired = models.BooleanField(default=False)
    requests_send = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email + " " + str(self.plan)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("User Subscriptions")


class FreeSubscriptions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="free_purchases")
    plan = models.ForeignKey(Plans, models.CASCADE, related_name="free_plan_purchases")
    is_expired = models.BooleanField(default=False)
    requests_send = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email + " " + str(self.plan)

    class Meta:
        verbose_name = _("Free Subscription")
        verbose_name_plural = _("Free User Subscriptions")


class UploadCoupons(models.Model):
    file = models.FileField(upload_to="Coupons")

    class Meta:
        verbose_name = _("Upload Coupon")
        verbose_name_plural = _("Upload Coupons")


class AllRequests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="all_requests")
    plan = models.ForeignKey(Plans, models.CASCADE, related_name="plan_requests")
    requests = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = _("Request")
        verbose_name_plural = _("All Requests")


class UploadTeams(models.Model):
    file = models.FileField(upload_to="Files/Teams")

    class Meta:
        verbose_name = _("Upload Team")
        verbose_name_plural = _("Upload Teams")


class ImageAnalysisDB(models.Model):
    file = models.ImageField(upload_to="Analysis/images", null=True, blank=True)


class VoiceCommands(models.Model):
    input = models.TextField()
    image = models.ImageField(upload_to="Commands/Images")

    def __str__(self):
        return self.input

    class Meta:
        verbose_name = _("Voice Command")
        verbose_name_plural = _("Voice Commands")


class PlatformChoices(models.TextChoices):
    OPENAI = "OPENAI", _('OPENAI')
    MICROSOFT = "MICROSOFT", _('MICROSOFT')


class KeyManagement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="keys")
    organization = models.CharField(max_length=100, null=True, blank=True)
    key = models.CharField(_("API Key"), max_length=200)
    endpoint = models.URLField(null=True, blank=True, max_length=200)
    platform = models.CharField(choices=PlatformChoices.choices, max_length=30, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email + " " + self.key

    class Meta:
        verbose_name = _("Open AI Key")
        verbose_name_plural = _("Open AI Keys")


class RestrictedKeywords(models.Model):
    community = models.ForeignKey(Community, related_name="keywords", on_delete=models.CASCADE)
    keyword = models.CharField(_("Keyword"), max_length=200, default="")
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.community.name + " " + self.keyword

    class Meta:
        verbose_name = _("Keyword")
        verbose_name_plural = _("Restricted Keywords")


class CapturedImages(models.Model):
    image = models.ImageField(upload_to="camera/images")


class CapturedAudio(models.Model):
    audio = models.FileField(upload_to="skybrain/audios")









