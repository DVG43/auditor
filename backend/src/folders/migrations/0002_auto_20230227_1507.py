# Generated by Django 3.2 on 2023-02-27 15:07

import django.contrib.postgres.fields
from django.db import migrations, models
import utils
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('folders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='folder',
            name='host_project',
        ),
        migrations.AddField(
            model_name='folder',
            name='doc_order',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.UUIDField(null=True), blank=True, default=list, size=None, verbose_name='Frame order'),
        ),
        migrations.AddField(
            model_name='folder',
            name='document_logo',
            field=models.ImageField(blank=True, null=True, upload_to=utils.get_doc_upload_path, verbose_name='Document logo'),
        ),
        migrations.AddField(
            model_name='folder',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]