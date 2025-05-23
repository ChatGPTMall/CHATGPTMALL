import uuid

from django.db import models

from engine.models import Items, ListingType
from skybrain.models import Room
from django.utils.translation import gettext_lazy as _

from users.models import User


# Create your models here.


class PlanType(models.TextChoices):
    FREE = "FREE", _('Free')
    BASIC = "BASIC", _('Basic')
    PREMIUM = "PREMIUM", _('Premium')


class HomePlans(models.Model):
    plan_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    home = models.ForeignKey(Room, related_name="room_plans", on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    plan_type = models.CharField(choices=PlanType.choices, max_length=30, default="FREE")
    features = models.JSONField(default=dict)
    price = models.FloatField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Home Plan")
        verbose_name_plural = _("Home Plans")

    def __str__(self):
        return str(self.plan_id)


class HomePlanPurchases(models.Model):
    user = models.ForeignKey(User, related_name="home_plans", on_delete=models.CASCADE)
    plan = models.ForeignKey(HomePlans, related_name="purchases", on_delete=models.PROTECT)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Home Plan Purchase")
        verbose_name_plural = _("Home Plan Purchases")

    def __str__(self):
        return str(self.user.email)


class HomepageNewFeature(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video = models.FileField(null=True, blank=True, upload_to="Homepage/videos")
    image = models.ImageField(upload_to="Homepage/images", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=50)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Homepage Content")
        verbose_name_plural = _("Homepage Content")


class FeaturesChoices(models.TextChoices):
    GENERAL = "GENERAL", _("General")
    TEXT_TO_TEXT = "TEXT_TO_TEXT", _("Text To Text")
    TEXT_TO_IMAGE = "TEXT_TO_IMAGE", _("Text To Image")
    VISION = "VISION", _("Vision")
    TAOBAO = "TAOBAO", _("Taobao")


class CreditsHistory(models.Model):
    credit_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, related_name="credits_history", on_delete=models.CASCADE)
    feature = models.CharField(choices=FeaturesChoices.choices, default=FeaturesChoices.GENERAL, max_length=20)
    tokens = models.FloatField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.credit_id)

    class Meta:
        verbose_name = _("Credit")
        verbose_name_plural = _("Credits Usage")

    @staticmethod
    def create_credits(user, tokens, feature):
        CreditsHistory.objects.create(user=user, tokens=tokens, feature=feature)


class WeChatAccounts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wechat_accounts")
    wechat_id = models.CharField(max_length=128)
    app_id = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("WeChat Account")
        verbose_name_plural = _("Add WeChat Accounts")


class RoomWhatsAppItems(models.Model):
    item = models.ForeignKey(Items, related_name="room_whatsapp", on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name="whatsapp_items", on_delete=models.CASCADE)
    listing = models.CharField(choices=ListingType.choices, default="GENERAL", max_length=20)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Room WhatsApp/Wechat Item")
        verbose_name_plural = _("Room WhatsApp/Wechat Items")


class VendingMachine(models.Model):
    machine_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    location = models.CharField(max_length=200)
    latitude = models.CharField(
        blank=True, null=True, help_text="Latitude for map integration.", max_length=30
    )
    longitude = models.CharField(
        blank=True, null=True, help_text="Longitude for map integration.", max_length=30
    )

    # Additional fields as needed, e.g. name, serial number, etc.

    def __str__(self):
        return f"{self.location} - {self.machine_id}"


class VendingMachineItem(models.Model):
    vending_machine = models.ForeignKey(VendingMachine, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    slot_number = models.PositiveIntegerField()  # or some way to track the position in the machine
    quantity = models.PositiveIntegerField(default=0)  # how many items of this kind are in that slot

    def __str__(self):
        return f"{self.item.title} in {self.vending_machine} (Slot {self.slot_number})"


class Mp3Files(models.Model):
    file = models.FileField(upload_to='mp3_files/')
    language = models.CharField(max_length=10, default='en')  # e.g., 'en', 'es', 'fr'
    recognized_text = models.TextField(blank=True, null=True)  # optional, store recognized speech

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mp3File(id={self.id}, language={self.language})"
