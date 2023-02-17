# Generated by Django 3.2 on 2022-10-25 13:39

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0017_remove_file_slugged_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='col_order',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None, verbose_name='Column order'),
        ),
        migrations.AddField(
            model_name='file',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='file',
            name='deleted_id',
            field=models.UUIDField(null=True, verbose_name='Deleted id'),
        ),
        migrations.AddField(
            model_name='file',
            name='deleted_since',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Deleted at'),
        ),
        migrations.AddField(
            model_name='file',
            name='description',
            field=models.TextField(blank=True, max_length=1000, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='file',
            name='frame_order',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None, verbose_name='Frame order'),
        ),
        migrations.AddField(
            model_name='file',
            name='last_modified_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Last modified at'),
        ),
        migrations.AddField(
            model_name='file',
            name='last_modified_user',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Last modified by'),
        ),
        migrations.AddField(
            model_name='file',
            name='name',
            field=models.CharField(default='', max_length=255, verbose_name='Title'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='link',
            name='col_order',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None, verbose_name='Column order'),
        ),
        migrations.AddField(
            model_name='link',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='link',
            name='deleted_id',
            field=models.UUIDField(null=True, verbose_name='Deleted id'),
        ),
        migrations.AddField(
            model_name='link',
            name='deleted_since',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Deleted at'),
        ),
        migrations.AddField(
            model_name='link',
            name='description',
            field=models.TextField(blank=True, max_length=1000, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='link',
            name='frame_order',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None, verbose_name='Frame order'),
        ),
        migrations.AddField(
            model_name='link',
            name='last_modified_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Last modified at'),
        ),
        migrations.AddField(
            model_name='link',
            name='last_modified_user',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Last modified by'),
        ),
        migrations.AddField(
            model_name='link',
            name='name',
            field=models.CharField(default='', max_length=255, verbose_name='Title'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='link',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
    ]
