# Generated by Django 3.2 on 2022-06-18 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0008_remove_contact_userfields'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together=set(),
        ),
    ]
