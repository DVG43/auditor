# Generated by Django 3.2 on 2022-06-13 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_auto_20220612_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfield',
            name='columnName',
            field=models.CharField(max_length=30, verbose_name='Column title'),
        ),
        migrations.AlterField(
            model_name='userfield',
            name='columnType',
            field=models.CharField(choices=[('text', 'Text'), ('select', 'Select choice'), ('email', 'Email'), ('phone', 'Phone'), ('image', 'Image'), ('time', 'Time')], max_length=10, verbose_name='Column type'),
        ),
        migrations.AlterField(
            model_name='userfield',
            name='model',
            field=models.CharField(max_length=20, verbose_name='Related model'),
        ),
        migrations.AlterField(
            model_name='userfieldmap',
            name='cellContent',
            field=models.TextField(blank=True, default='', verbose_name='Content'),
        ),
        migrations.AlterModelTable(
            name='userfield',
            table='ppm_usercolumns',
        ),
        migrations.AlterModelTable(
            name='userfieldmap',
            table='ppm_usercolumns_content',
        ),
    ]
