# Generated by Django 3.2 on 2023-02-15 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0024_auto_20221129_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.CharField(blank=True, max_length=50, verbose_name='Address'),
        ),
    ]
