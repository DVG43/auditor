# Generated by Django 3.2 on 2022-11-17 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0029_school_promocode'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocode',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='sertificatepayment',
            name='created_at',
            field=models.BigIntegerField(null=True, verbose_name='Payment timestamp'),
        ),
    ]
