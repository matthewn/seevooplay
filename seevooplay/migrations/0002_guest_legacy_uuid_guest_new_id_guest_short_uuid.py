import shortuuid.django_fields
from django.db import migrations, models


def populate_short_uuids(apps, schema_editor):
    import shortuuid
    su = shortuuid.ShortUUID()
    Guest = apps.get_model("seevooplay", "Guest")
    for guest in Guest.objects.all():
        guest.short_uuid = su.random(length=16)
        guest.save(update_fields=["short_uuid"])


class Migration(migrations.Migration):
    dependencies = [
        ("seevooplay", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="guest",
            name="legacy_uuid",
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="guest",
            name="new_id",
            field=models.IntegerField(null=True),
        ),
        # Add short_uuid WITHOUT unique constraint first
        migrations.AddField(
            model_name="guest",
            name="short_uuid",
            field=shortuuid.django_fields.ShortUUIDField(
                alphabet=None,
                editable=False,
                length=16,
                max_length=16,
                prefix="",
            ),
        ),
        # Populate unique values for each row
        migrations.RunPython(populate_short_uuids, migrations.RunPython.noop),
        # Now add the unique constraint
        migrations.AlterField(
            model_name="guest",
            name="short_uuid",
            field=shortuuid.django_fields.ShortUUIDField(
                alphabet=None,
                editable=False,
                length=16,
                max_length=16,
                prefix="",
                unique=True,
            ),
        ),
    ]
