# Generated by Django 3.2 on 2022-06-04 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storyboards', '0003_auto_20220603_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chrono',
            name='frames',
        ),
        migrations.DeleteModel(
            name='ChronoFrame',
        ),
    ]
