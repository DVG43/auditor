# Generated by Django 3.2 on 2022-06-25 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0013_usercell_choiceid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usercell',
            options={'ordering': ['id'], 'verbose_name': 'Usercolumn data', 'verbose_name_plural': 'Usercolumn data'},
        ),
        migrations.AlterModelOptions(
            name='userchoice',
            options={'ordering': ['id'], 'verbose_name': 'Choice for select field', 'verbose_name_plural': 'Choices for select field'},
        ),
        migrations.AlterModelOptions(
            name='usercolumn',
            options={'ordering': ['id'], 'verbose_name': 'User column', 'verbose_name_plural': 'User columns'},
        ),
    ]
