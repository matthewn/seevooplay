# Generated by Django 3.2.4 on 2021-06-09 04:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seevooplay', '0008_alter_guest_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='raw_guests',
            new_name='invitees',
        ),
    ]
