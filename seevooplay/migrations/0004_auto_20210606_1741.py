# Generated by Django 3.2.4 on 2021-06-07 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seevooplay', '0003_alter_event_end_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='image_height',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='image_width',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]