# Generated by Django 3.2 on 2022-07-04 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscription', '0004_auto_20220704_0943'),
    ]

    operations = [
        migrations.CreateModel(
            name='TPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='Tax payer id')),
                ('title', models.CharField(max_length=255, verbose_name='Tax payer title')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tpids', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Tax payer id',
                'verbose_name_plural': 'Tax payer ids',
            },
        ),
        migrations.AlterModelOptions(
            name='banktransfer',
            options={'verbose_name': 'Bank transfer', 'verbose_name_plural': 'Bank transfers'},
        ),
        migrations.AlterModelOptions(
            name='cardpayment',
            options={'verbose_name': 'Card payment', 'verbose_name_plural': 'Card payments'},
        ),
        migrations.AlterModelOptions(
            name='currency',
            options={'verbose_name': 'Currency', 'verbose_name_plural': 'Currencies'},
        ),
        migrations.AlterModelOptions(
            name='paymentdetails',
            options={'verbose_name': 'Payment details', 'verbose_name_plural': 'Payment details'},
        ),
        migrations.AlterModelOptions(
            name='paymentmethod',
            options={'verbose_name': 'Payment method', 'verbose_name_plural': 'Payment methods'},
        ),
        migrations.AlterModelOptions(
            name='promocode',
            options={'verbose_name': 'Promocode', 'verbose_name_plural': 'Promocodes'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Subscription', 'verbose_name_plural': 'Subscriptions'},
        ),
        migrations.AlterModelOptions(
            name='tariff',
            options={'verbose_name': 'Tariff', 'verbose_name_plural': 'Tariffs'},
        ),
        migrations.AlterModelOptions(
            name='tariffperiod',
            options={'verbose_name': 'Tariff period', 'verbose_name_plural': 'Tariff periods'},
        ),
        migrations.DeleteModel(
            name='Inn',
        ),
    ]
