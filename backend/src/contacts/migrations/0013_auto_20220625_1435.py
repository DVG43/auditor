# Generated by Django 3.2 on 2022-06-25 14:35

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0012_auto_20220625_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='colOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='position',
            name='colOrder',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
    ]
