# Generated by Django 3.2 on 2022-10-14 13:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0013_alter_project_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('url', models.URLField(max_length=255, verbose_name='Ссылка')),
                ('tag_color', models.CharField(blank=True, default='', max_length=20, verbose_name='Plate color')),
                ('host_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='projects.project')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('title', 'url')},
            },
        ),
    ]
