# Generated by Django 3.2 on 2022-06-25 16:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('callsheets', '0026_auto_20220620_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callsheet',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='callsheetmember',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='location',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
    ]
