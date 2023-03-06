# Generated by Django 3.2 on 2023-03-01 07:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # ('document', '0014_alter_document_host_project'),
        ('folders', '0002_auto_20230227_1507'),
        ('table', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='defaulttablemodel',
            name='host_document_id',
        ),
        migrations.RemoveField(
            model_name='defaulttablemodel',
            name='host_document_model',
        ),
        migrations.AddField(
            model_name='defaulttablemodel',
            name='host_document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='document.document'),
        ),
        migrations.AddField(
            model_name='defaulttablemodel',
            name='host_folder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='folders.folder'),
        ),
    ]