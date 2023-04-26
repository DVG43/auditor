# Generated by Django 3.2 on 2023-04-25 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0015_auto_20230421_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='datequestion',
            name='date_answer_mode',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AddField(
            model_name='datequestion',
            name='time_answer_mode',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AlterField(
            model_name='datequestion',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='datequestion',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
