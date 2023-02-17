# Generated by Django 3.2 on 2022-06-08 10:12

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shootingplans', '0004_auto_20220603_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='shootingplan',
            name='colOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='shootingplan',
            name='frameOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='unit',
            name='colOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='unit',
            name='frameOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='unitframe',
            name='colOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='unitframe',
            name='frameOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
    ]
