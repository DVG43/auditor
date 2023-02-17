import re
import uuid

from io import BytesIO
from PIL import Image
from django.contrib.postgres.fields import ArrayField
from django.core.files.base import ContentFile, File
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from django.utils.crypto import get_random_string

from accounts.utils import get_upload_path


class ResizeImageMixin:
    @staticmethod
    def resize(imagefield: models.ImageField, size: tuple):
        im = Image.open(imagefield)  # Catch original
        source_image = im.convert('RGB')
        source_image.thumbnail(size)  # Resize to size
        output = BytesIO()
        source_image.save(output, format='JPEG')  # Save resize image to bytes
        output.seek(0)
        # Read output and create ContentFile in memory
        content_file = ContentFile(output.read())
        file = File(content_file)

        random_name = f'{uuid.uuid4()}.jpeg'
        imagefield.save(random_name, file, save=False)


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        first_name='PPM-User',
        last_name='PPM-User',
        password=get_random_string(length=16),
        is_staff=False,
        is_superuser=False
    ):
        # if not email:
        #     raise ValueError('email required')
        if email:
            email = self.normalize_email(email)
        else:
            email = first_name + get_random_string(length=8) + '@ppm.ru'
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        user.is_verified = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password=None):
        return self.create_user(email, password, True, False)

    def create_superuser(self, email, password,
                         first_name='admin', last_name='admin', is_verified=True):
        return self.create_user(first_name, last_name, email, password, True, True)


class User(AbstractBaseUser, ResizeImageMixin):
    USER_LANGUAGE = (
        ('ru', _('Russian')),
        ('eng', _('English')),
    )
    pkid = models.BigAutoField('№', primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.CharField(_('Address'), max_length=50, unique=True)
    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50, blank=True)
    phone = models.CharField(_('Phone'), max_length=15, blank=True, null=True)
    birthday = models.DateField(_('Birth date'), blank=True, null=True)
    code = models.CharField(
        _('Verification code'), max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(_('Is verified'), default=False)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    avatar = models.ImageField(
        _('Avatar'), upload_to=get_upload_path, null=True)
    is_active = models.BooleanField(_('Is active'), default=True)
    is_staff = models.BooleanField(_('Staff status'), default=False)
    is_superuser = models.BooleanField(_('Superuser status'), default=False)
    changed_password_date = models.DateTimeField(
        _('changed_password_date'),
        auto_now_add=True,
        blank=True,
        null=True
    )
    user_language = models.CharField(
        _('User language'),
        max_length=4,
        choices=USER_LANGUAGE,
        default='ru'
    )
    # subscription

    b24_contact_id = models.IntegerField(null=True, blank=True)
    b24_deal_id = models.IntegerField(null=True, blank=True)

    like = models.BooleanField(_('Promo bordomatic like'), default=False)
    document_like = models.BooleanField(_('Promo document like'), default=False)
    document = models.UUIDField(null=True)
    is_invited = models.BooleanField(_('Is invited'), default=False)

    disk_space = models.BigIntegerField(_('Used disk space'), default=0,
                                        null=True)

    contacts_order = ArrayField(
        models.IntegerField(blank=True), blank=True, default=list, verbose_name=_('Data row order'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['pkid']

    def __str__(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        if self.pk is None and self.avatar:
            self.resize(self.avatar, (200, 200))
        if re.fullmatch(r'\d\d.\d\d.\d{4}', str(self.birthday)):
            dd, mm, yyyy = self.birthday.split('.')
            self.birthday = f'{yyyy}-{mm}-{dd}'
        super().save(*args, **kwargs)
