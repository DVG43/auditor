# Generated by Django 3.2 on 2023-01-25 20:16

import django.contrib.postgres.fields
from django.db import migrations, models
import utils
import uuid

def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model('document', 'Document')
    for row in MyModel.objects.all():
        row.order_id = uuid.uuid4()
        row.save(update_fields=['order_id'])

class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_alter_element_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='document_logo',
            field=models.ImageField(blank=True, null=True, upload_to=utils.get_doc_upload_path, verbose_name='Document logo'),
        ),
        migrations.AddField(
            model_name='document',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='document',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, null=True, unique=True),
        ),
    ]
