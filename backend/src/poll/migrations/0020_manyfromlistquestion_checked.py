# Generated by Django 3.2 on 2023-04-28 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0019_auto_20230426_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='manyfromlistquestion',
            name='checked',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]