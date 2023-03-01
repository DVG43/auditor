
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import ResizeImageMixin
from objectpermissions.registration import register
from objectpermissions.models import ModelPermissions

from utils import get_icon_upload_path

# permissions = ['read', 'edit', 'own', 'delete']
permissions = ['read', 'edit', 'own']
PERMS = ModelPermissions(permissions)


class PpmDocModel(models.Model):
    class Meta:
        abstract = True

    owner = models.ForeignKey(
        'accounts.User', verbose_name=_('Owner'), on_delete=models.CASCADE)
    name = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True, max_length=1000)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    last_modified_user = models.EmailField(
        _('Last modified by'), null=True, blank=True)
    last_modified_date = models.DateTimeField(
        _('Last modified at'), auto_now=True)
    deleted_id = models.UUIDField(_('Deleted id'), null=True)
    deleted_since = models.DateTimeField(
        _('Deleted at'), null=True, blank=True)
    tag_color = models.CharField(
        _('Plate color'), max_length=20, blank=True, default='')
    data_row_order = ArrayField(
        models.IntegerField(blank=True),
        blank=True,
        default=list,
        verbose_name=_('Data row order')
    )
    col_order = ArrayField(
        models.IntegerField(blank=True),
        blank=True,
        default=list,
        verbose_name=_('Column order')
    )


class UserColumn(models.Model):
    USERCOLUMN_TYPES = (
        ('text', _('Text')),
        ('select', _('Select choice')),
        ('multiselect', _('Multiselect choice')),
        ('numbers', _("Numbers")),
        ('email', _('Email')),
        ('phone', _('Phone')),
        ('image', _('Image')),
        ('time', _('Time')),
        ('contact', _('Contact')),
        ('tablelink', _("Link to table"))
    )
    column_name = models.CharField(
        _('Column title'), max_length=30, blank=False, null=False)
    column_type = models.CharField(
        _('Column type'), choices=USERCOLUMN_TYPES, max_length=11)
    # choices
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('Owner'))
    # cells
    is_visible = models.BooleanField(_("Is visible"), default=True)

    class Meta:
        db_table = 'ppm_usercolumns'
        ordering = ['id']
        verbose_name = _('User column')
        verbose_name_plural = _('User columns')


class UserChoice(models.Model):
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    choice = models.CharField(max_length=100, blank=True)
    host_usercolumn = models.ForeignKey(
        UserColumn, on_delete=models.CASCADE, related_name='choices')
    color = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        db_table = 'ppm_usercolumns_choices'
        ordering = ['id']
        verbose_name = _('Choice for select field')
        verbose_name_plural = _('Choices for select field')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        user_cells = UserCell.objects.filter(choice_id=self)
        if user_cells:
            for uc in user_cells:
                uc.cell_content = self.choice
                uc.save()


class UserCell(models.Model):
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('Owner'))
    host_usercolumn = models.ForeignKey(
        UserColumn,
        on_delete=models.CASCADE,
        null=True,
        related_name='cells',
        verbose_name=_('User column'))
    cell_content = models.TextField(_('Content'), blank=True, default="", max_length=1000)
    choice_id = models.ForeignKey(
        UserChoice,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Choice id')
    )
    choices_id = ArrayField(
        models.IntegerField(blank=True),
        blank=True,
        default=list,
        verbose_name=_('Choices id')
    )

    # images

    class Meta:
        db_table = 'ppm_usercolumns_contents'
        ordering = ['id']
        verbose_name = _('Usercolumn data')
        verbose_name_plural = _('Usercolumn data')

    def __str__(self):
        return f'CELL#{self.id}'


class UsercellImage(models.Model, ResizeImageMixin):
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    host_usercell = models.ForeignKey(
        UserCell,
        on_delete=models.SET_NULL,
        null=True,
        related_name='images'
    )
    file = models.ImageField(
        upload_to='usercell_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is None and self.file:
            self.resize(self.file, (1920, 1080))
        super().save(*args, **kwargs)

class StandardIcon(models.Model, ResizeImageMixin):
    """Model of standard icon that present on the site.
    The user can use any of the standard icons to choose as the logo of his project or document.
    """
    icon_image = models.ImageField(upload_to=get_icon_upload_path,
                                   verbose_name='image')
    created_at = models.DateTimeField(verbose_name='сreated at', auto_now_add=True)
    is_active = models.BooleanField(verbose_name='is active', default=True)

    class Meta:
        """Ordering objects according to their id.
        """
        ordering = ('id',)
        verbose_name = 'Стандартная иконка'
        verbose_name_plural = 'Стандартные иконки'

    def __str__(self):
        """Forms and returns a printable representation of the object.
        """
        return f'Icon {self.id}'

register(UserColumn, permissions)
register(UserCell, permissions)
register(UserChoice, permissions)
register(UsercellImage, permissions)
register(StandardIcon, permissions)
