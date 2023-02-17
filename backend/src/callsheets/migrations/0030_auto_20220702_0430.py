# Generated by Django 3.2 on 2022-07-02 04:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('callsheets', '0029_alter_callsheetmember_userfields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='callsheet',
            old_name='breakEnd',
            new_name='break_end',
        ),
        migrations.RenameField(
            model_name='callsheet',
            old_name='breakStart',
            new_name='break_start',
        ),
        migrations.RenameField(
            model_name='callsheet',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='callsheet',
            old_name='currentLunch',
            new_name='current_lunch',
        ),
        migrations.RenameField(
            model_name='callsheet',
            old_name='endTime',
            new_name='end_time',
        ),
        migrations.RenameField(
            model_name='callsheet',
            old_name='filmDay',
            new_name='film_day',
        ),
        migrations.RenameField(
            model_name='callsheet',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='callsheet',
            old_name='shiftType',
            new_name='shift_type',
        ),
        migrations.RenameField(
            model_name='callsheet',
            old_name='startTime',
            new_name='start_time',
        ),
        migrations.RenameField(
            model_name='callsheet',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='callsheetlogo',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='callsheetlogo',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='callsheetlogo',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='callsheetmember',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='callsheetmember',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='callsheetmember',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='checkIn',
            new_name='check_in',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='checkOut',
            new_name='check_out',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='shiftType',
            new_name='shift_type',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='startMotor',
            new_name='start_motor',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='stopMotor',
            new_name='stop_motor',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='tagColor',
            new_name='tag_color',
        ),
        migrations.RenameField(
            model_name='locationmap',
            old_name='colOrder',
            new_name='col_order',
        ),
        migrations.RenameField(
            model_name='locationmap',
            old_name='frameOrder',
            new_name='frame_order',
        ),
        migrations.RenameField(
            model_name='locationmap',
            old_name='tagColor',
            new_name='tag_color',
        ),
    ]
