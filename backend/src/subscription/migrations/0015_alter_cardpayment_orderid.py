# Generated by Django 3.2 on 2022-09-02 11:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0014_auto_20220902_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardpayment',
            name='OrderId',
            field=models.UUIDField(default=uuid.UUID('028b9d98-43dd-403f-af01-27b09f61fd7a')),
        ),
    ]
