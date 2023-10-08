import uuid

from django.db import models

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
