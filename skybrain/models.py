import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryChoices(models.TextChoices):
    HOTEL = "HOTEL", _('Hotel')
    SCHOOL = "SCHOOL", _('School')
    SHOP = "SHOP", _('Shop')
    HOSPITAL = "HOSPITAL", _('Hospital')


class Organization(models.Model):
    name = models.CharField(unique=True, max_length=200)
    image = models.ImageField(null=True, blank=True, upload_to="Organizations/Logo")
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
    organization = models.ForeignKey(Organization, related_name="rooms", on_delete=models.CASCADE, null=True, blank=True)
    room_id = models.CharField(max_length=200)
    room_key = models.CharField(max_length=200, null=True, blank=True)
    custom_instructions = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_id

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")
        unique_together = (("organization", "room_id"), ("room_id", "room_key"))


class RoomKeys(models.Model):
    room = models.ForeignKey(Room, related_name="keys", on_delete=models.CASCADE)
    room_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.CharField(unique=True, max_length=200, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.room_key)

    class Meta:
        verbose_name = _("Room Key")
        verbose_name_plural = _("Room Keys")
        unique_together = (("room_key", "room", "email"),)


class RoomItems(models.Model):
    room = models.ForeignKey(Room, to_field="id", related_name="room_items", on_delete=models.CASCADE)
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
    room = models.ForeignKey(Room, related_name="room_support", on_delete=models.CASCADE)
    user_input = models.TextField()
    response = models.TextField()
    cs_response = models.TextField(null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    has_replied = models.BooleanField(default=False)

    def __str__(self):
        return str(self.room)


class Favourites(models.Model):
    room = models.ForeignKey(Room, related_name="favourites", on_delete=models.CASCADE)
    history_id = models.IntegerField(default=0)
    user_input = models.TextField()
    response = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user_input)

    class Meta:
        verbose_name = _("Favourite")
        verbose_name_plural = _("Favourites")


class Unsubscribe(models.Model):
    email = models.CharField(unique=True, max_length=100)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = _("Unsubscribe")
        verbose_name_plural = _("Unsubscribed")


class CustomInstructions(models.Model):
    room = models.ForeignKey(Room, related_name="suggestions", on_delete=models.CASCADE)
    suggestion_one = models.TextField()
    suggestion_two = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Custom Instruction")
        verbose_name_plural = _("Custom Instructions")
