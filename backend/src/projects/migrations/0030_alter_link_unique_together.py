# Generated by Django 3.2 on 2022-12-19 09:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0029_auto_20221209_1216'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='link',
            unique_together=set(),
        ),
    ]
