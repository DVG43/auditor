# Generated by Django 3.2 on 2022-06-17 12:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_alter_project_table'),
        ('contacts', '0008_remove_contact_userfields'),
        ('callsheets', '0012_auto_20220617_1221'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CallsheetMember',
        ),
    ]
