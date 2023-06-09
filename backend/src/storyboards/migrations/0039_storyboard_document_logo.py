# Generated by Django 3.2 on 2022-12-19 08:53

from django.db import migrations, models
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('storyboards', '0038_auto_20221129_0952'),
    ]

    operations = [
        migrations.AddField(
            model_name='storyboard',
            name='document_logo',
            field=models.ImageField(blank=True, null=True, upload_to=utils.get_doc_upload_path, verbose_name='Document logo'),
        ),
    ]
