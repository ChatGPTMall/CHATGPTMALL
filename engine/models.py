import random
import string
from django.db import models
from users.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _


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
    user = models.OneToOneField(User, related_name='team', on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Community Members")


class CommunityPosts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    community = models.ForeignKey(Community, related_name="feed", on_delete=models.CASCADE)
    question = models.TextField(_("User Question"), unique=True)
    response = models.TextField(_("AI Response"))
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = _("Community Post")
        verbose_name_plural = _("Community Posts")
