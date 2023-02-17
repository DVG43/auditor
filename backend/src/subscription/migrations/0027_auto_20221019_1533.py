# Generated by Django 3.2 on 2022-10-19 15:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscription', '0026_alter_subscription_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='tariff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscription.tariff', verbose_name='Tariff'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
