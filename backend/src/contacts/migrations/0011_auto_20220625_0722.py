# Generated by Django 3.2 on 2022-06-25 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0010_auto_20220619_1707'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='department',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='position',
            unique_together=set(),
        ),
    ]
