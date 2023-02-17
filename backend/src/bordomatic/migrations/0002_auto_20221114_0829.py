# Generated by Django 3.2 on 2022-11-14 08:29

from django.db import migrations, models
import storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('bordomatic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bordomaticprivate',
            name='fps',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ФПС'),
        ),
        migrations.AddField(
            model_name='bordomaticprivate',
            name='height',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Ширина'),
        ),
        migrations.AddField(
            model_name='bordomaticprivate',
            name='width',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Длина'),
        ),
        migrations.AlterField(
            model_name='bordomatic',
            name='fps',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ФПС'),
        ),
        migrations.AlterField(
            model_name='bordomatic',
            name='height',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Ширина'),
        ),
        migrations.AlterField(
            model_name='bordomatic',
            name='uploaded_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата загрузки'),
        ),
        migrations.AlterField(
            model_name='bordomatic',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Видео'),
        ),
        migrations.AlterField(
            model_name='bordomatic',
            name='width',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Длина'),
        ),
        migrations.AlterField(
            model_name='bordomaticprivate',
            name='uploaded_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата загрузки'),
        ),
        migrations.AlterField(
            model_name='bordomaticprivate',
            name='video',
            field=models.FileField(blank=True, null=True, storage=storage_backends.PrivateMediaStorage(), upload_to='', verbose_name='Видео'),
        ),
    ]
