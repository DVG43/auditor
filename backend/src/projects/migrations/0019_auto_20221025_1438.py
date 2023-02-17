# Generated by Django 3.2 on 2022-10-25 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0018_auto_20221025_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to='projects/files/', verbose_name='File'),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together={('name', 'file')},
        ),
        migrations.AlterUniqueTogether(
            name='link',
            unique_together={('name', 'url')},
        ),
        migrations.RemoveField(
            model_name='file',
            name='title',
        ),
        migrations.RemoveField(
            model_name='link',
            name='title',
        ),
    ]
