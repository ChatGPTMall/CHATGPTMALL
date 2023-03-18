from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


class Category(models.Model):
    title = models.CharField(max_length=200)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Item Categories")

    def __str__(self):
        return self.title


class Items(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="images/items/", null=True, blank=True)
    price = models.FloatField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

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


class Plans(models.Model):
    title = models.CharField(max_length=200)
    price = models.FloatField(default=0)
    plan_type = models.CharField(choices=PlanType.choices, max_length=30, default="MONTHLY")
    description = models.TextField()
    requests = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Subscription Plan")
        verbose_name_plural = _("Chatgptmall Plans")





