from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import permissions, PpmDocModel
from objectpermissions.registration import register


class Contact(PpmDocModel):
    name = models.CharField(_('Name Surname'), max_length=100, blank=True)
    position = models.ForeignKey(
        'Position',
        verbose_name=_('Position'),
        on_delete=models.SET_NULL,
        null=True, blank=True)
    department = models.ForeignKey(
        'Department',
        verbose_name=_('Department'),
        on_delete=models.SET_NULL,
        null=True, blank=True)
    phone = models.CharField(_('Phone'), max_length=15, blank=True)
    email = models.CharField(_('Address'), max_length=50, blank=True)
    # in_projects

    class Meta:
        db_table = 'ppm_contacts'
        ordering = ['id']
        verbose_name = _('Crew member')
        verbose_name_plural = _('Crew members')

    def __str__(self):
        return f'CNT#{self.id} {self.name}'


class Position(PpmDocModel):
    name = models.CharField(
        _('Title'), max_length=100, default=_('Position'))
    tag_color = models.CharField(
        _('Plate color'), max_length=10, blank=True)

    class Meta:
        db_table = 'ppm_contacts_positions'
        ordering = ['id']
        verbose_name = _('Position')
        verbose_name_plural = _('Positions')

    def __str__(self):
        return f'POS#{self.id} {self.name}'


class Department(PpmDocModel):
    name = models.CharField(
        _('Title'), max_length=100, default=_('Department'))
    tag_color = models.CharField(_('Plate color'), max_length=10, blank=True)

    class Meta:
        db_table = 'ppm_contacts_departments'
        ordering = ['id']
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')

    def __str__(self):
        return f'{self.name} ({self.id})'


register(Contact, permissions)
register(Position, permissions)
register(Department, permissions)
