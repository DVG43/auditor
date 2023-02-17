# Generated by Django 3.2 on 2023-02-03 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_user_changed_password_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_language',
            field=models.CharField(choices=[('ru', 'Russian'), ('eng', 'English')], default='ru', max_length=4, verbose_name='User language'),
        ),
    ]
