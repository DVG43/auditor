# Generated by Django 3.2 on 2022-08-29 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0020_alter_contact_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(blank=True, default=' ', max_length=255, verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(blank=True, default=' ', max_length=100, verbose_name='Name Surname'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(blank=True, default=' ', max_length=15, verbose_name='Phone'),
            preserve_default=False,
        ),
    ]
