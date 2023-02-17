# Generated by Django 3.2 on 2022-07-18 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_auto_20220718_1144'),
        ('trash', '0004_auto_20220629_0605'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trash',
            old_name='in_trash_since',
            new_name='deleted_since',
        ),
        migrations.RemoveField(
            model_name='trash',
            name='project_id',
        ),
        migrations.RemoveField(
            model_name='trash',
            name='project_name',
        ),
        migrations.AddField(
            model_name='trash',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='projects.project'),
            preserve_default=False,
        ),
    ]
