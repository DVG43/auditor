# Generated by Django 3.2 on 2022-06-17 12:34

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0008_remove_contact_userfields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('callsheets', '0013_delete_callsheetmember'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallsheetMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('last_modified_user', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Last modified by')),
                ('last_modified_date', models.DateTimeField(auto_now=True, verbose_name='Last modified at')),
                ('is_in_trash', models.BooleanField(default=False, verbose_name='Is deleted')),
                ('in_trash_since', models.DateTimeField(blank=True, null=True, verbose_name='Deleted at')),
                ('tagColor', models.CharField(blank=True, default='', max_length=20, verbose_name='Plate color')),
                ('frameOrder', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None)),
                ('colOrder', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None)),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contacts.department')),
                ('host_callsheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='callsheets.callsheet')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contacts.position')),
                ('userfields', models.ManyToManyField(blank=True, related_name='of_callsheets', to='contacts.Contact')),
            ],
            options={
                'db_table': 'ppm_callsheets_members',
            },
        ),
    ]
