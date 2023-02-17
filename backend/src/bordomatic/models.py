from django.db import models
from django.utils.translation import gettext_lazy as _

from storage_backends import PrivateMediaStorage
from storyboards.models import Storyboard
from common.models import permissions
from objectpermissions.registration import register


class Bordomatic(models.Model):
    storyboard = models.ForeignKey(Storyboard, on_delete=models.CASCADE,
                                   verbose_name=_("Сториборд"), related_name='bordomatic')

    video = models.FileField(_("Видео"), blank=True, null=True)
    uploaded_at = models.DateTimeField(_("Дата загрузки"), auto_now=True)

    fps = models.PositiveIntegerField(_("ФПС"), blank=True, null=True)
    width = models.PositiveIntegerField(_("Длина"), blank=True, null=True)
    height = models.PositiveIntegerField(_("Ширина"), blank=True, null=True)

    class Meta:
        verbose_name = 'Бордоматик'
        verbose_name_plural = 'Бордоматики'

    def __str__(self):
        return f'{self.storyboard_id}__{self.video.name}'


class BordomaticPrivate(models.Model):
    storyboard = models.ForeignKey(Storyboard, on_delete=models.CASCADE,
                                   verbose_name=_("Сториборд"), related_name='bordomatic_private')

    video = models.FileField(_("Видео"), storage=PrivateMediaStorage(), blank=True, null=True)
    uploaded_at = models.DateTimeField(_("Дата загрузки"), auto_now=True)

    fps = models.PositiveIntegerField(_("ФПС"), blank=True, null=True)
    width = models.PositiveIntegerField(_("Длина"), blank=True, null=True)
    height = models.PositiveIntegerField(_("Ширина"), blank=True, null=True)

    class Meta:
        verbose_name = 'Приватный бордоматик'
        verbose_name_plural = 'Приватные бордоматики'

    def __str__(self):
        return f'{self.storyboard_id}__{self.video.name}'


choises_effectname = [
    ("zoomIn", "zoomIn"),
    ("zoomOut", "zoomOut"),
    ("moveTop", " moveTop"),
    ("moveLeft", " moveLeft"),
    ("moveRight", "moveRight"),
    ("moveBottom", "moveBottom")
]
choises_effectvalue = (
    ("1x", "1x"), ("2x", "2x"), ("3x", "3x"), ("4x", "4x"), ("5x", "5x"), ("6x", "6x"), ("7x", "7x"), ("8x", "8x"),
    ("9x", "9x"), ("10x", "10x"),
    ("11x", "11x"), ("12x", "12x"), ("13x", "13x"), ("14x", "14x"), ("15x", "15x"), ("16x", "16x"),
    ("10%", "10%"), ("20%", "20%"), ("30%", "30%"), ("40%", "40%"), ("50%", "50%"),
    ("60%", "60%"), ("70%", "70%"), ("80%", "80%"), ("90%", "90%"), ("100%", "100%")
)


class ImageForBordomatic(models.Model):
    bordomatic = models.ForeignKey(Bordomatic, on_delete=models.CASCADE,
                                   verbose_name=_("Картинка для бордоматика"),
                                   related_name='images')

    image = models.FileField(_("Картинка"))
    frame_time = models.PositiveIntegerField(_("Время кадра"))  # время кадра в бордоматике
    effectValue = models.CharField(
        _("Парамер эффекта"),
        max_length=30,
        choices=choises_effectvalue,
        null=True,
        blank=True
    )
    effectName = models.CharField(
        _("Наименование эффекта"),
        max_length=30,
        blank=True,
        choices=choises_effectname,
        null=True
    )
    subtitle = models.CharField(_("Субтитр"), max_length=255)
    subtitleView = models.BooleanField(_("Парамер эффекта"))

    uploaded_at = models.DateTimeField(_("Дата загрузки"), auto_now_add=True)


class ImageForBordomaticPrivate(models.Model):
    bordomatic = models.ForeignKey(BordomaticPrivate, on_delete=models.CASCADE,
                                   verbose_name=_("Картинка для бордоматика (Приват)"),
                                   related_name='images')

    image = models.FileField(_("Картинка"), storage=PrivateMediaStorage())
    frame_time = models.PositiveIntegerField(_("Время кадра"))  # время кадра в бордоматике
    effectValue = models.CharField(
        _("Парамер эффекта"),
        max_length=30,
        choices=choises_effectvalue,
        blank=True,
        null=True
    )
    effectName = models.CharField(
        _("Наименование эффекта"),
        max_length=30,
        choices=choises_effectname,
        blank=True,
        null=True
    )
    subtitle = models.CharField(_("Субтитр"), max_length=255)
    subtitleView = models.BooleanField(_("Парамер эффекта"), max_length=255)
    uploaded_at = models.DateTimeField(_("Дата загрузки"), auto_now_add=True)


class AudioForBordomatic(models.Model):
    bordomatic = models.ForeignKey(Bordomatic, on_delete=models.CASCADE,
                                   verbose_name=_("Аудио для бордоматика"),
                                   related_name='audios')

    audio = models.FileField(_("Аудио"))
    name_audio = models.CharField(_("Имя аудиофайла"), max_length=255)
    uploaded_at = models.DateTimeField(_("Дата загрузки"), auto_now_add=True)

    begin = models.CharField(_("Начало"), max_length=255)
    end = models.CharField(_("Конец"), max_length=255)
    volume = models.FloatField(_("Громкость"))


class AudioForBordomaticPrivate(models.Model):
    bordomatic = models.ForeignKey(BordomaticPrivate, on_delete=models.CASCADE,
                                   verbose_name=_("Аудио для бордоматика (Приват)"),
                                   related_name='audios')

    audio = models.FileField(_("Аудио"), storage=PrivateMediaStorage())
    name_audio = models.CharField(_("Имя аудиофайла"), max_length=255)
    uploaded_at = models.DateTimeField(_("Дата загрузки"), auto_now_add=True)

    begin = models.CharField(_("Начало"), max_length=255)
    end = models.CharField(_("Конец"), max_length=255)
    volume = models.FloatField(_("Громкость"))


register(BordomaticPrivate, permissions)
register(Bordomatic, permissions)
