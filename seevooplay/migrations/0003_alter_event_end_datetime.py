# Generated by Django 3.2.4 on 2021-06-07 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seevooplay', '0002_auto_20210607_0031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]