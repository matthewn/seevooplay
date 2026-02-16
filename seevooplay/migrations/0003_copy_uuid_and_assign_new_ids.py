from django.db import migrations


def populate_legacy_and_new_ids(apps, schema_editor):
    Guest = apps.get_model("seevooplay", "Guest")
    for i, guest in enumerate(Guest.objects.order_by('created'), start=1):
        guest.legacy_uuid = guest.id  # copy UUID before it's gone
        guest.new_id = i  # assign sequential integer based on creation order
        guest.save(update_fields=["legacy_uuid", "new_id"])


def reverse_populate(apps, schema_editor):
    Guest = apps.get_model("seevooplay", "Guest")
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(seevooplay_guest)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'new_id' in columns:
            Guest.objects.all().update(legacy_uuid=None, new_id=None)
        else:
            # column was already removed by migration 0004, just clear legacy_uuid
            Guest.objects.all().update(legacy_uuid=None)


class Migration(migrations.Migration):
    dependencies = [
        ("seevooplay", "0002_guest_legacy_uuid_guest_new_id_guest_short_uuid"),
    ]

    operations = [
        migrations.RunPython(populate_legacy_and_new_ids, reverse_populate),
    ]
