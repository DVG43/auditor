# Generated by Django 3.2 on 2023-01-29 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0007_auto_20230125_2316'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='document',
            table='ppm_documents',
        ),
        migrations.AlterModelTable(
            name='element',
            table='ppm_documents_elements',
        ),
        migrations.AlterModelTable(
            name='tagfordocument',
            table='ppm_documents_tags',
        ),
    ]
