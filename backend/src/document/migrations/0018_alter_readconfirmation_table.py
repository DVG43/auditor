# Generated by Django 3.2 on 2023-04-18 07:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0017_auto_20230418_1003'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='readconfirmation',
            table='ppm_documents_confirmations',
        ),
    ]
