# Generated by Django 3.2 on 2022-06-18 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shootingplans', '0015_rename_unitframe_columns_unit_columns'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unit',
            old_name='columns',
            new_name='frame_columns',
        ),
    ]
