# Generated by Django 3.2.5 on 2021-09-11 01:20

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import djrichtextfield.models
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=64)),
                ('host1_name', models.CharField(max_length=128)),
                ('host1_email', models.EmailField(max_length=254)),
                ('host2_name', models.CharField(blank=True, max_length=128)),
                ('host2_email', models.EmailField(blank=True, max_length=254)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('location_name', models.CharField(max_length=64)),
                ('location_address', models.CharField(blank=True, max_length=128)),
                ('details', djrichtextfield.models.RichTextField(blank=True)),
                ('image', models.ImageField(blank=True, upload_to='event_images/')),
                ('invitees', models.TextField(blank=True, help_text='\n            Enter a list of email addresses separated by commas or new lines.\n            <br>You can put full names before email addresses, and we\'ll try to\n            figure the whole mess out.\n            <br>Quotes and angle brackets will be ignored. Example input:\n            <pre>    prince@example.org, madonna@example.org</pre>\n            <pre>    "Rip Torn" &lt;rip_torn@example.org&gt;</pre>\n            <pre>    Tim Berners Lee tim@example.org</pre>\n            <big><b><i>New invitees will be immediately emailed!</b></i></big>\n        ')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('has_viewed', models.BooleanField(default=False)),
                ('status', models.CharField(blank=True, choices=[('Y', 'Yes'), ('N', 'No'), ('M', 'Maybe')], max_length=1)),
                ('extra_guests', models.PositiveSmallIntegerField(default=0)),
                ('comment', models.CharField(blank=True, max_length=512)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seevooplay.event')),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seevooplay.guest')),
            ],
            options={
                'verbose_name_plural': 'Replies',
                'ordering': ('guest',),
            },
        ),
        migrations.AddField(
            model_name='event',
            name='guests',
            field=models.ManyToManyField(blank=True, through='seevooplay.Reply', to='seevooplay.Guest', verbose_name='Invited guests'),
        ),
    ]
