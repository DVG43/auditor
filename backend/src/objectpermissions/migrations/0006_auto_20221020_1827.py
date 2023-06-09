# Generated by Django 3.2 on 2022-10-20 18:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('objectpermissions', '0005_alter_userpermission_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpermission',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='contenttypes.contenttype', verbose_name='Content type'),
        ),
        migrations.AlterField(
            model_name='userpermission',
            name='object_id',
            field=models.PositiveIntegerField(verbose_name='Objects id'),
        ),
        migrations.AlterField(
            model_name='userpermission',
            name='permission',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Permission'),
        ),
        migrations.AlterField(
            model_name='userpermission',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
