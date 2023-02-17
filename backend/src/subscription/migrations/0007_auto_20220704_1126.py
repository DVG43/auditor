# Generated by Django 3.2 on 2022-07-04 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0006_auto_20220704_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='banktransfer',
            name='date',
            field=models.BigIntegerField(default=1, verbose_name='Payment timestamp'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cardpayment',
            name='date',
            field=models.BigIntegerField(default=1, verbose_name='Payment timestamp'),
            preserve_default=False,
        ),
    ]
