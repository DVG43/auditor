import uuid

from django.db import models
from django.db.models import ImageField
from django.utils.translation import gettext_lazy as _

from accounts.models import ResizeImageMixin
from common.models import PpmDocModel, permissions
from objectpermissions.registration import register
from utils import get_doc_upload_path


class Callsheet(PpmDocModel):
    LUNCH_TYPES = (
        ('c', _('Current')),
        ('h', _('Hour'))
    )
    name = models.CharField(_('Name'),
                            max_length=50, default=_('Callsheet'))
    host_project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='callsheets',
        verbose_name=_('Project'))
    date = models.DateField(_('Date'))
    film_day = models.CharField(
        _('Film day number'),
        blank=True,
        max_length=20,
        default=""
    )
    start_time = models.TimeField(_('Start time'), blank=True, default="00:00")
    end_time = models.TimeField(_('Finish time'), blank=True, default="00:00")
    lunch_type = models.CharField(
        _('Lunch type'),
        choices=LUNCH_TYPES,
        max_length=1,
        blank=True,
        default=''
    )
    lunch_time = models.CharField(
        _('Lunch time'),
        max_length=50,
        blank=True,
        default=''
    )
    shift_type = models.CharField(
        _('Shift type'),
        max_length=2,
        default='',
        blank=True
    )
    contact = models.TextField(
        _('Contact'),
        blank=True,
        default="",
        max_length=300
    )
    sunrise = models.TimeField(_('Sunrise'), default="00:00")
    sunset = models.TimeField(_('Sunset'), default="00:00")
    temp = models.CharField(_('Temperature'), max_length=20, default="0")
    max_temp = models.CharField(
        _('Max temperature'),
        max_length=20,
        default="0"
    )
    min_temp = models.CharField(
        _('Min temperature'),
        max_length=20,
        default="0"
    )
    weather = models.CharField(_('Weather'), max_length=200, blank=True)
    city = models.CharField(_('City'), max_length=200, blank=True)
    lat = models.FloatField(_('Latitude'), default=0.0, blank=True)
    lng = models.FloatField(_('Longitude'), default=0.0, blank=True)
    userfields = models.ManyToManyField(
        'common.UserCell',
        blank=True,
        related_name='in_callsheet'
    )
    usercolumns = models.ManyToManyField(
        'common.UserColumn',
        blank=True,
        related_name='of_callsheet'
    )
    member_columns = models.ManyToManyField(
        'common.UserColumn',
        blank=True,
        related_name='of_callsheetmember'
    )
    doc_uuid = models.UUIDField(editable=False, unique=True,
                                null=True)
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)
    document_logo = ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='callsheets',
        verbose_name=_('Folder'),
        blank=True, null=True
    )

    # callsheet_logos
    # members

    class Meta:
        db_table = 'ppm_callsheets'
        ordering = ['id']
        verbose_name = _('Callsheet')
        verbose_name_plural = _('Callsheets')

    def __str__(self):
        return f"CALLSHEET#{self.id}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = uuid.uuid4()
        return super().save(*args, **kwargs)


class Callsheetmember(PpmDocModel):
    name = models.CharField(max_length=255, blank=True)
    position = models.ForeignKey(
        'contacts.Position',
        on_delete=models.SET_NULL,
        null=True, blank=True)
    department = models.ForeignKey(
        'contacts.Department',
        on_delete=models.SET_NULL,
        null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    host_callsheet = models.ForeignKey(
        Callsheet,
        on_delete=models.CASCADE,
        related_name='members'
    )
    userfields = models.ManyToManyField(
        'common.UserCell',
        blank=True,
        related_name='of_callsheetmember'
    )

    class Meta:
        db_table = 'ppm_callsheets_members'
        verbose_name = _('Callsheet member')
        verbose_name_plural = _('Callsheet members')


class Location(PpmDocModel):
    host_callsheet = models.ForeignKey(
        Callsheet,
        on_delete=models.CASCADE,
        related_name='locations')
    address = models.CharField(_('Address'), max_length=255, blank=True)
    check_in = models.TimeField(_('Check-in'), blank=True, default="00:00")
    check_out = models.TimeField(_('Check-out'), blank=True, default="00:00")
    start_motor = models.TimeField(_('Action'), blank=True, default="00:00")
    stop_motor = models.TimeField(_('Cut'), blank=True, default="00:00")
    shift_type = models.CharField(_('Shift type'), max_length=2, default='', blank=True)
    userfields = models.ManyToManyField(
        'common.UserCell',
        blank=True,
        related_name='in_location'
    )
    usercolumns = models.ManyToManyField(
        'common.UserColumn',
        blank=True,
        related_name='of_location'
    )

    # maps

    class Meta:
        db_table = 'ppm_callsheets_locations'
        ordering = ['id']
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')

    def __str__(self):
        return f"LOCATION#{self.id}"


class LocationMap(PpmDocModel, ResizeImageMixin):
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('Owner'))
    host_location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='maps')
    file = models.ImageField(
        upload_to=get_doc_upload_path,
        null=True, blank=True,
        verbose_name=_('File'))

    class Meta:
        db_table = 'ppm_callsheets_locations_maps'
        verbose_name = _('Location map')
        verbose_name_plural = _('Location maps')

    def __str__(self):
        return f"MAP#{self.id}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.resize(self.file, (800, 600))
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super().delete(*args, **kwargs)


class CallsheetLogo(PpmDocModel):
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('Owner'))
    host_callsheet = models.ForeignKey(
        Callsheet,
        on_delete=models.CASCADE,
        related_name='callsheet_logos')
    file = models.ImageField(
        upload_to=get_doc_upload_path,
        null=True, blank=True,
        verbose_name=_('File'))

    class Meta:
        db_table = 'ppm_callsheets_logos'
        verbose_name = _('Callsheet logo')
        verbose_name_plural = _('Callsheet logos')

    def __str__(self):
        return f'LOGO#{self.id}'

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super().delete(*args, **kwargs)


register(Callsheet, permissions)
register(Location, permissions)
register(LocationMap, permissions)
register(CallsheetLogo, permissions)
register(Callsheetmember, permissions)
