# Generated by Django 3.2 on 2022-11-10 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objectpermissions', '0006_auto_20221020_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermission',
            name='datetime',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
