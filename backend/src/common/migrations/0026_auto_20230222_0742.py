# Generated by Django 3.2 on 2023-02-22 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0025_usercell_choices_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercolumn',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='Is visible'),
        ),
        migrations.AlterField(
            model_name='usercolumn',
            name='column_type',
            field=models.CharField(choices=[('text', 'Text'), ('select', 'Select choice'), ('multiselect', 'Multiselect choice'), ('numbers', 'Numbers'), ('email', 'Email'), ('phone', 'Phone'), ('image', 'Image'), ('time', 'Time'), ('contact', 'Contact'), ('tablelink', 'Link to table')], max_length=11, verbose_name='Column type'),
        ),
    ]