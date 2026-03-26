from django.db import migrations, models


def set_existing_replies_as_sent(apps, schema_editor):
    Reply = apps.get_model('seevooplay', 'Reply')
    Reply.objects.all().update(invitation_sent=True)


class Migration(migrations.Migration):

    dependencies = [
        ('seevooplay', '0005_alter_guest_legacy_uuid_alter_guest_short_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='invitation_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            set_existing_replies_as_sent,
            migrations.RunPython.noop,
        ),
    ]
