# Generated by Django 3.2 on 2023-03-10 06:14
import uuid

from django.db import migrations


def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model('table', 'DefaultTableModel')
    for row in MyModel.objects.all():
        row.order_id = uuid.uuid4()
        row.save(update_fields=['order_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('table', '0003_auto_20230309_1336'),
    ]

    operations = [
        migrations.RunPython(gen_uuid),
    ]
