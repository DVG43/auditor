# Generated by Django 3.2 on 2022-06-30 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='paymentMethod',
            field=models.CharField(choices=[('card', 'Credit/debit card'), ('bill', 'Invoice')], max_length=4, verbose_name='Payment method'),
        ),
    ]
