# Generated by Django 3.2 on 2023-02-07 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_user_changed_password_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=50, unique=True, verbose_name='Address'),
        ),
    ]
