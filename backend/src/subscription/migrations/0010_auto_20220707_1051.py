# Generated by Django 3.2 on 2022-07-07 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0009_auto_20220707_0656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banktransfer',
            name='promocode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.promocode'),
        ),
        migrations.AlterField(
            model_name='cardpayment',
            name='promocode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.promocode'),
        ),
    ]
