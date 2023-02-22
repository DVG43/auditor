import os
from os.path import join, isfile
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, \
    RegexValidator
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from poll.models.poll import Poll


def file_path(instance, file_name):
    file_name = f'{file_name}'
    file_locate = join('theme/images', f'user_{instance.user.pk}', file_name)
    return file_locate


class PollTheme(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='pollsthemes', blank=True, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='themes',
                             blank=True, null=True)

    name = models.CharField(max_length=255)
    article = models.CharField(max_length=255, default='', blank=True, null=True)

    logo = models.ImageField(upload_to=file_path, blank=True, null=True)
    logo_name = models.CharField(max_length=255, default='', blank=True, null=True)
    logo_color_active = models.BooleanField(default=True, blank=True, null=True)
    logo_bg_color = models.CharField(max_length=7,
                                validators=[RegexValidator(regex="#([a-fA-F0-9]){3,6}")], blank=True, null=True)

    background_name = models.CharField(max_length=255, default='', blank=True, null=True)
    background_image = models.ImageField(upload_to=file_path, blank=True, null=True)
    background_opacity = models.DecimalField(max_digits=3, decimal_places=2,
                                             validators=[MinValueValidator(0),
                                                         MaxValueValidator(1)],
                                             default=1, blank=True, null=True)
    is_standard = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    setting_font_family = models.CharField(max_length=255, default='', blank=True)
    setting_text_color = models.CharField(max_length=255, default='', blank=True)
    setting_element_color = models.CharField(max_length=255, default='', blank=True)
    setting_background_color = models.CharField(max_length=255, default='', blank=True)
    settings_progress_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'poll_theme'
        verbose_name = _('Poll theme')
        verbose_name_plural = _('Polls themes')

    def __str__(self):
        return self.name


def _delete_file(path):
    if isfile(path):
        os.remove(path)


@receiver(models.signals.post_delete, sender=PollTheme)
def delete_file(sender, instance, *args, **kwargs):
    if instance.user:
        profile = instance.user.secretguestprofile
        if instance.logo:
            logo_size = instance.logo.size
            _delete_file(instance.logo.path)
            profile.current_disk_space_decrement(logo_size)
        if instance.background_image:
            background_image_size = instance.background_image.size
            _delete_file(instance.background_image.path)
            profile.current_disk_space_decrement(background_image_size)
