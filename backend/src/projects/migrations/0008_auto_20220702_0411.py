# Generated by Django 3.2 on 2022-07-02 04:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_remove_project_uid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='tagColor',
            new_name='tag_color',
        ),
    ]
