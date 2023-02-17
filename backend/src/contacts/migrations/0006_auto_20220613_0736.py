# Generated by Django 3.2 on 2022-06-13 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20220613_0614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callsheetcalltime',
            name='time',
            field=models.TimeField(blank=True, default='00:00'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(blank=True, default=1, max_length=254),
            preserve_default=False,
        ),
    ]
