# Generated by Django 3.2 on 2022-06-18 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_rename_field_usercell_column'),
        ('storyboards', '0014_alter_frame_userfields'),
    ]

    operations = [
        migrations.AddField(
            model_name='storyboard',
            name='frame_columns',
            field=models.ManyToManyField(blank=True, related_name='of_storyboard', to='common.UserColumn'),
        ),
    ]
