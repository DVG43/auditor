# Generated by Django 3.2 on 2022-11-15 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bordomatic', '0003_auto_20221115_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audioforbordomatic',
            name='begin',
            field=models.CharField(max_length=255, verbose_name='Начало'),
        ),
        migrations.AlterField(
            model_name='audioforbordomatic',
            name='end',
            field=models.CharField(max_length=255, verbose_name='Конец'),
        ),
        migrations.AlterField(
            model_name='audioforbordomaticprivate',
            name='begin',
            field=models.CharField(max_length=255, verbose_name='Начало'),
        ),
        migrations.AlterField(
            model_name='audioforbordomaticprivate',
            name='end',
            field=models.CharField(max_length=255, verbose_name='Конец'),
        ),
    ]
