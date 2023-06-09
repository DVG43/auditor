# Generated by Django 3.2 on 2022-09-12 13:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0021_alter_cardpayment_orderid'),
    ]

    operations = [
        migrations.AddField(
            model_name='tinkoffresponse',
            name='RebillId',
            field=models.CharField(default=0, max_length=255, verbose_name='ID рекуррентного платежа'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cardpayment',
            name='OrderId',
            field=models.UUIDField(default=uuid.UUID('cdf3aa00-a54a-42fe-8265-dec91298c2f2')),
        ),
    ]
