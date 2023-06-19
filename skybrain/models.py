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
    is_approved = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.organization

    class Meta:
        verbose_name = _("Room Request")
        verbose_name_plural = _("Room Requests")


class Room(models.Model):
    organization = models.ForeignKey(Organization, related_name="rooms", on_delete=models.CASCADE)
    room_id = models.CharField(unique=True, max_length=30)
    room_key = models.CharField(unique=True, max_length=200, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_id

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")


class RoomHistory(models.Model):
    room = models.ForeignKey(Room, related_name="history", on_delete=models.CASCADE)
    user_input = models.TextField()
    response = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.room)

    class Meta:
        verbose_name = _("Room History")
        verbose_name_plural = _("Room History")


class RoomItems(models.Model):
    room = models.ForeignKey(Room, to_field="room_id", related_name="room_items", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default="ROOM Item")
    image = models.ImageField(upload_to="Room/Items", null=True, blank=True)
    video = models.FileField(upload_to="Room/Videos", null=True, blank=True)
    description = models.TextField(null=True)
    price = models.IntegerField(default=0)
    is_private = models.BooleanField(default=False)
    category = models.CharField(max_length=100)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.room)

    class Meta:
        verbose_name = _("Room Item")
        verbose_name_plural = _("Room Items")


class CustomerSupport(models.Model):
    room = models.ForeignKey(Room, related_name="history", on_delete=models.CASCADE)
    user_input = models.TextField()
    response = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    has_replied = models.BooleanField(default=False)

    def __str__(self):
        return str(self.room)
