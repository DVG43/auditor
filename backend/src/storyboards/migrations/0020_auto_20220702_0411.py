# Generated by Django 3.2 on 2022-07-02 04:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storyboards', '0019_alter_shot_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chrono',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='chrono',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='chrono',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='chronoframe',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='chronoframe',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='chronoframe',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='frame',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='frame',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='frame',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='shot',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='shot',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='shot',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='storyboard',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='storyboard',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='storyboard',
            old_name='tagColor',
            new_name='tag_color',
        ),
    ]
