# Generated by Django 3.2 on 2022-06-03 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storyboards', '0002_auto_20220603_0227'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chrono',
            name='sortOrder',
        ),
        migrations.RemoveField(
            model_name='chronoframe',
            name='sortOrder',
        ),
        migrations.RemoveField(
            model_name='frame',
            name='sortOrder',
        ),
        migrations.RemoveField(
            model_name='shot',
            name='sortOrder',
        ),
        migrations.RemoveField(
            model_name='storyboard',
            name='sortOrder',
        ),
    ]
