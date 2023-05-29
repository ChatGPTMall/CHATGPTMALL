from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryChoices(models.TextChoices):
    HOTEL = "HOTEL", _('Hotel')
    SCHOOL = "SCHOOL", _('School')
    SHOP = "SHOP", _('Shop')
    HOSPITAL = "HOSPITAL", _('Hospital')


class Organization(models.Model):
    name = models.CharField(unique=True, max_length=200)
    category = models.CharField(choices=CategoryChoices.choices, default="HOTEL", max_length=20)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")


class LicensesRequests(models.Model):
    organization = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    no_of_licenses = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.organization

    class Meta:
        verbose_name = _("Room Request")
        verbose_name_plural = _("Room Requests")


class Room(models.Model):
    organization = models.ForeignKey(Organization, related_name="rooms", on_delete=models.CASCADE)
    room_id = models.CharField(unique=True, max_length=30)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_id

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")