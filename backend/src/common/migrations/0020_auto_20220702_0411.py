# Generated by Django 3.2 on 2022-07-02 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0019_auto_20220630_0536'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercell',
            old_name='cellContent',
            new_name='cell_content',
        ),
        migrations.RenameField(
            model_name='usercell',
            old_name='choiceId',
            new_name='choice_id',
        ),
        migrations.RenameField(
            model_name='usercolumn',
            old_name='columnName',
            new_name='column_name',
        ),
        migrations.RemoveField(
            model_name='usercolumn',
            name='columnType',
        ),
        migrations.AddField(
            model_name='usercolumn',
            name='column_type',
            field=models.CharField(choices=[('text', 'Text'), ('select', 'Select choice'), ('email', 'Email'), ('phone', 'Phone'), ('image', 'Image'), ('time', 'Time'), ('contact', 'Contact')], default='text', max_length=10, verbose_name='Column type'),
            preserve_default=False,
        ),
    ]
