# Generated by Django 3.2 on 2022-06-04 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_alter_userfield_choices'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userfieldmap',
            options={'get_latest_by': 'id'},
        ),
    ]
