# Generated by Django 3.2 on 2022-06-21 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0009_auto_20220618_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='userchoice',
            name='color',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]
