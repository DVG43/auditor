# Generated by Django 3.2 on 2022-06-13 07:36

import django.contrib.postgres.fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('callsheets', '0008_auto_20220613_0614'),
    ]

    operations = [
        migrations.AddField(
            model_name='callsheetlogo',
            name='colOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='callsheetlogo',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='callsheetlogo',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='callsheetlogo',
            name='frameOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='callsheetlogo',
            name='in_trash_since',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Deleted at'),
        ),
        migrations.AddField(
            model_name='callsheetlogo',
            name='is_in_trash',
            field=models.BooleanField(default=False, verbose_name='Is deleted'),
        ),
        migrations.AddField(
            model_name='callsheetlogo',
            name='last_modified_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Last modified at'),
        ),
        migrations.AddField(
            model_name='callsheetlogo',
            name='last_modified_user',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Last modified by'),
        ),
        migrations.AddField(
            model_name='callsheetlogo',
            name='name',
            field=models.CharField(default=1, max_length=255, verbose_name='Title'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='callsheetlogo',
            name='tagColor',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Plate color'),
        ),
        migrations.AddField(
            model_name='locationmap',
            name='colOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='locationmap',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='locationmap',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='locationmap',
            name='frameOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='locationmap',
            name='in_trash_since',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Deleted at'),
        ),
        migrations.AddField(
            model_name='locationmap',
            name='is_in_trash',
            field=models.BooleanField(default=False, verbose_name='Is deleted'),
        ),
        migrations.AddField(
            model_name='locationmap',
            name='last_modified_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Last modified at'),
        ),
        migrations.AddField(
            model_name='locationmap',
            name='last_modified_user',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Last modified by'),
        ),
        migrations.AddField(
            model_name='locationmap',
            name='name',
            field=models.CharField(default=1, max_length=255, verbose_name='Title'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='locationmap',
            name='tagColor',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Plate color'),
        ),
    ]
