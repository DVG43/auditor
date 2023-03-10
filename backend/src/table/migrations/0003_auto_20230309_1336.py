# Generated by Django 3.2 on 2023-03-09 13:36

from django.db import migrations, models
import utils
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('table', '0002_auto_20230301_0704'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaulttablemodel',
            name='doc_uuid',
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='defaulttablemodel',
            name='document_logo',
            field=models.ImageField(blank=True, null=True, upload_to=utils.get_doc_upload_path, verbose_name='Document logo'),
        ),
        migrations.AddField(
            model_name='defaulttablemodel',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]