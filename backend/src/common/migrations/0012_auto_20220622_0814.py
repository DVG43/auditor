# Generated by Django 3.2 on 2022-06-22 08:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0011_alter_usercolumn_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usercell',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='userchoice',
            options={'ordering': ['id']},
        ),
    ]
