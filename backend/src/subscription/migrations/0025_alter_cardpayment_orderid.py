# Generated by Django 3.2 on 2022-09-23 03:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0024_auto_20220915_0404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardpayment',
            name='OrderId',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
