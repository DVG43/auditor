# Generated by Django 3.2 on 2022-06-03 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ['id']},
        ),
        migrations.RemoveField(
            model_name='contact',
            name='sortOrder',
        ),
        migrations.RemoveField(
            model_name='department',
            name='sortOrder',
        ),
        migrations.RemoveField(
            model_name='position',
            name='sortOrder',
        ),
    ]
