# Generated by Django 3.2 on 2022-06-13 05:32

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('callsheets', '0006_auto_20220608_1012'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CSLogo',
            new_name='CallsheetLogo',
        ),
        migrations.AlterField(
            model_name='callsheet',
            name='name',
            field=models.CharField(default='Callsheet', max_length=50),
        ),
        migrations.AlterField(
            model_name='callsheet',
            name='shiftType',
            field=models.CharField(choices=[('interior', 'Interior'), ('exterior', 'Exterior')], default='interior', max_length=8),
        ),
        migrations.AlterField(
            model_name='location',
            name='shiftType',
            field=models.CharField(choices=[('interior', 'Interior'), ('exterior', 'Exterior')], default='interior', max_length=8),
        ),
        migrations.AlterModelTable(
            name='callsheet',
            table='ppm_callsheets',
        ),
        migrations.AlterModelTable(
            name='callsheetlogo',
            table='ppm_callsheets_logos',
        ),
        migrations.AlterModelTable(
            name='location',
            table='ppm_callsheets_locations',
        ),
        migrations.AlterModelTable(
            name='locationmap',
            table='ppm_callsheets_locations_maps',
        ),
    ]
