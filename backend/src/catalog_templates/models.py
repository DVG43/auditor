from django.db import models

# Create your models here.
from django.db import models, IntegrityError, router, transaction
from common.models import PpmDocModel, permissions
from django.utils.translation import gettext_lazy as _
from objectpermissions.registration import register
from django.conf import settings
from django.utils.text import slugify

try:
    from unidecode import unidecode
except ImportError:
    from .utils import slugify as unidecode
    # def unidecode(category)
    #     return category

class Template(models.Model):
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
    template_text = models.TextField(verbose_name=_("Template text"), default="")
    example = models.TextField(verbose_name=_("Example"), default="")
    result = models.TextField(verbose_name=_("Result"), default="")
    is_common = models.BooleanField(_('Is common'), default=False)
    favourite = models.ManyToManyField('accounts.User', blank=True, related_name='favourite_templates')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'ppm_templates'
        ordering = ['id']

class CategoryForTemplate(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100, unique=True)
    slug = models.SlugField(
        verbose_name=_("Slug"),
        unique=True,
        max_length=100,
        allow_unicode=True,
    )
    templates = models.ManyToManyField(Template, blank=True, related_name='categories')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding and not self.slug:
            self.slug = self.slugify(self.name)
            using = kwargs.get("using") or router.db_for_write(
                type(self), instance=self
            )
            # Make sure we write to the same db for all attempted writes,
            # with a multi-master setup, theoretically we could try to
            # write and rollback on different DBs
            kwargs["using"] = using
            # Be opportunistic and try to save the tag, this should work for
            # most cases ;)
            try:
                with transaction.atomic(using=using):
                    res = super().save(*args, **kwargs)
                return res
            except IntegrityError:
                pass
            # Now try to find existing slugs with similar names
            slugs = set(
                type(self)._default_manager.filter(slug__startswith=self.slug)
                .values_list("slug", flat=True)
            )
            i = 1
            while True:
                slug = self.slugify(self.name, i)
                if slug not in slugs:
                    self.slug = slug
                    # We purposely ignore concurrency issues here for now.
                    # (That is, till we found a nice solution...)
                    return super().save(*args, **kwargs)
                i += 1
        else:
            return super().save(*args, **kwargs)

    def slugify(self, category, i=None):
        if getattr(settings, "TAGGIT_STRIP_UNICODE_WHEN_SLUGIFYING", False):
            slug = slugify(unidecode(category))
        else:
            slug = slugify(category, allow_unicode=True)
        if i is not None:
            slug += "_%d" % i
        return slug

    class Meta:
        db_table = 'ppm_templates_categories'
        ordering = ['id']


register(Template, permissions)
