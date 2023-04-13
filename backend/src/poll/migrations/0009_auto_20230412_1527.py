# Generated by Django 3.2 on 2023-04-12 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0008_auto_20230407_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='manyfromlistquestion',
            name='answer_mode',
            field=models.IntegerField(choices=[('ONE', 1), ('SOME', 2)], default=1),
        ),
        migrations.AlterField(
            model_name='checkquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='datequestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='divisionquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='finalquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='freeanswer',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='manyfromlistquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='mediaquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='numberquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='pagequestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='ratingquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='sectionquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='textquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
        migrations.AlterField(
            model_name='yesnoquestion',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poll.poll'),
        ),
    ]