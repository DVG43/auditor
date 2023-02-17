# Generated by Django 3.2 on 2022-06-03 02:27
import django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storyboards', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chronoframe',
            options={},
        ),
        migrations.AlterField(
            model_name='chrono',
            name='frames',
            field=models.ManyToManyField(blank=True, related_name='in_chronos',
                                         through='storyboards.ChronoFrame',
                                         to='storyboards.Frame'),
        ),
        migrations.AlterModelOptions(
            name='frame',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='storyboard',
            options={'ordering': ['id']},
        ),
        migrations.RenameField(
            model_name='chronoframe',
            old_name='host_chrono',
            new_name='chrono',
        ),
        migrations.AlterField(
            model_name='frame',
            name='host_storyboard',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='frames',
                                    to='storyboards.storyboard'),
        ),
    ]
