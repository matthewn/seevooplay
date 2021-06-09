# Generated by Django 3.2.4 on 2021-06-09 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seevooplay', '0018_alter_event_invitees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='invitees',
            field=models.TextField(blank=True, help_text='Enter a list of email addresses separated by commas or new lines. You can put full names before email addresses, and we\'ll try to figure the whole mess out. Quotes and angle brackets will be ignored. Example input:<pre>    prince@example.org</pre>, madonna@example.org</pre><pre>    "Rip Torn" rip_torn@example.org</pre><pre>    Tim Berners Lee tim@example.org</pre><b><i>New invitees will be immediately emailed!</b></i>'),
        ),
    ]
