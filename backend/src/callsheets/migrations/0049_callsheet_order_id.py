# Generated by Django 3.2 on 2022-11-18 12:36

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('callsheets', '0048_merge_0046_auto_20221102_1503_0047_auto_20221109_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='callsheet',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]
