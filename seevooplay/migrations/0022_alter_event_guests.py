# Generated by Django 3.2.4 on 2021-06-09 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seevooplay', '0021_alter_event_invitees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='guests',
            field=models.ManyToManyField(blank=True, to='seevooplay.Guest', verbose_name='Invited guests'),
        ),
    ]