# Generated by Django 3.2 on 2023-03-10 06:17

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0026_auto_20230222_0742'),
        ('table', '0005_auto_20230310_0614'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultTableUsercell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cell_content', models.TextField(blank=True, default='', max_length=1000, verbose_name='Content')),
                ('choices_id', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None, verbose_name='Choices id')),
                ('choice_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.userchoice', verbose_name='Choice id')),
                ('frame_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='table.defaulttableframe', verbose_name='Frame')),
                ('host_usercolumn', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='table_cells', to='common.usercolumn', verbose_name='User column')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
            ],
            options={
                'verbose_name': 'Table usercolumn data',
                'verbose_name_plural': 'Table usercolumn data',
                'db_table': 'table_usercolumns_contents',
                'ordering': ['id'],
            },
        ),
    ]
