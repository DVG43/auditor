# Generated by Django 3.2 on 2022-09-12 15:34

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_beat', '0016_alter_crontabschedule_timezone'),
        ('subscription', '0022_auto_20220912_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='recurrent_payment_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_celery_beat.periodictask'),
        ),
        migrations.AlterField(
            model_name='cardpayment',
            name='OrderId',
            field=models.UUIDField(default=uuid.UUID('dadd35de-7a21-44b3-aa7b-97d2945c975f')),
        ),
    ]
