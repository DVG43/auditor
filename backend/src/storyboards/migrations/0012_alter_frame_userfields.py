# Generated by Django 3.2 on 2022-06-17 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_auto_20220613_0614'),
        ('storyboards', '0011_auto_20220613_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frame',
            name='userfields',
            field=models.ManyToManyField(blank=True, related_name='in_frames', to='common.UserFieldMap'),
        ),
    ]
