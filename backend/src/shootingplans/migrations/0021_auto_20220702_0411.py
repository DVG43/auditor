# Generated by Django 3.2 on 2022-07-02 04:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shootingplans', '0020_auto_20220626_0335'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shootingplan',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='shootingplan',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='shootingplan',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='unit',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='unit',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='unit',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='unitframe',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='unitframe',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='unitframe',
            old_name='tagColor',
            new_name='tag_color',
        ),
    ]
