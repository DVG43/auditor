# Generated by Django 3.2 on 2022-06-30 16:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
        ('accounts', '0005_user_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='subscription',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to='subscription.subscription', verbose_name='Subscription info'),
        ),
    ]
