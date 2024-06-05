import uuid
import string
import random
from django.db import models
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from skybrain.models import Room


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


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class LowercaseEmailField(models.EmailField):
    """
    Override EmailField to convert emails to lowercase before saving.
    """

    def to_python(self, value):
        value = super(LowercaseEmailField, self).to_python(value)
        if value:
            return value.lower()
        return value


def set_name(instance, filename):
    """
    """
    ext = filename.split('.')[-1]
    if instance.pk:
        return '{}.{}'.format(instance.user_id, ext)
    else:
        pass
        # do something if pk is not there yet


class PremiumFlags(models.IntegerChoices):
    FREE_USER = (0, _('Free User'))
    PREMIUM_USER = (1, _('Premium User'))
    KEY_USER = (2, _('Key Admin User'))


class AccessTypes(models.TextChoices):
    NO_ACCESS = "NO_ACCESS", _('No Access')
    TEXT_TO_TEXT = "TEXT_TO_TEXT", _('Text To Text')
    VOICE_TO_Voice = "VOICE_TO_Voice", _('Voice To Voice')
    VOICE_TO_IMAGE = "VOICE_TO_IMAGE", _('Voice To Image')
    TEXT_TO_IMAGE = "TEXT_TO_IMAGE", _('Text To Image')


class User(AbstractBaseUser, PermissionsMixin):
    """
    User Table, which will provide login functionality
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Required:
        email
        password
        first_name
        last_name
        phone_no
    """
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=150, null=True)
    email = LowercaseEmailField(_('email address'), unique=True)
    access = models.CharField(choices=AccessTypes.choices, max_length=30, default="TEXT_TO_TEXT")
    phone_no = PhoneNumberField(null=True, default=None, blank=True, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    reset_token = models.CharField(_('Reset Token'), max_length=5, default=0)
    user_id = models.UUIDField(default=uuid.uuid4, unique=True)
    room = models.ForeignKey(Room, related_name="room", on_delete=models.PROTECT, null=True, blank=True)
    premium = models.IntegerField(choices=PremiumFlags.choices, default=0)
    joined_on = models.DateTimeField(auto_now_add=True)
    credits = models.IntegerField(default=5)
    purchased_on = models.DateTimeField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    country = models.CharField(null=True, blank=True, max_length=100)
    postal_code = models.CharField(null=True, blank=True, max_length=100)
    wechat_ids = models.JSONField(default=list)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """To send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def is_temp_email(self):
        """
        If temp email assigned to this user
        as signed up using phone_no
        """
        return self.email.endswith("@chatgptmall.com")

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_access(self):
        user = User.objects.get(email=self.email)
        if user.purchases.filter(user__email=self.email).exists():
            has_access = True


class ChinaUsers(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, unique=True)
    room = models.ForeignKey(Room, related_name="wechat_room", on_delete=models.PROTECT, null=True, blank=True)
    wechat_id = models.CharField(_("WeChat ID"), unique=True, max_length=100)
    joined_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('China User')
        verbose_name_plural = _('China User')


class UploadUsers(models.Model):
    file = models.FileField(upload_to="Users")

    class Meta:
        verbose_name = _("Upload User")
        verbose_name_plural = _("Upload Users")


class RoomHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="home_history", null=True)
    room = models.ForeignKey(Room, related_name="history", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="openai/gpt_4", null=True, blank=True)
    user_input = models.TextField()
    response = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.room)

    class Meta:
        verbose_name = _("Room History")
        verbose_name_plural = _("Room History")
