from django.db import migrations, models


def swap_pk_sqlite(apps, schema_editor):
    """SQLite-specific: rebuild tables with new integer PK"""
    with schema_editor.connection.cursor() as cursor:
        # disable foreign keys for this operation
        cursor.execute("PRAGMA foreign_keys = OFF")

        # create new guest table with integer PK
        cursor.execute("""
            CREATE TABLE new__seevooplay_guest (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                created datetime NOT NULL,
                modified datetime NOT NULL,
                name varchar(64) NOT NULL,
                email varchar(254) NOT NULL UNIQUE,
                short_uuid varchar(22) NOT NULL UNIQUE,
                legacy_uuid char(32) NULL
            )
        """)

        # copy data using new_id as the new id
        cursor.execute("""
            INSERT INTO new__seevooplay_guest
                (id, created, modified, name, email, short_uuid, legacy_uuid)
            SELECT
                new_id, created, modified, name, email, short_uuid, legacy_uuid
            FROM seevooplay_guest
            WHERE new_id IS NOT NULL
        """)

        # Create new reply table with integer guest_id FK
        cursor.execute("""
            CREATE TABLE new__seevooplay_reply (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                created datetime NOT NULL,
                modified datetime NOT NULL,
                has_viewed bool NOT NULL,
                status varchar(1) NOT NULL,
                extra_guests integer NOT NULL,
                comment varchar(512) NOT NULL,
                event_id integer NOT NULL,
                guest_id integer NOT NULL,
                FOREIGN KEY (event_id) REFERENCES seevooplay_event (id) DEFERRABLE INITIALLY DEFERRED,
                FOREIGN KEY (guest_id) REFERENCES new__seevooplay_guest (id) DEFERRABLE INITIALLY DEFERRED
            )
        """)

        # copy reply data, mapping UUID guest_id to new integer
        cursor.execute("""
            INSERT INTO new__seevooplay_reply
                (id, created, modified, has_viewed, status,
                 extra_guests, comment, event_id, guest_id)
            SELECT
                r.id, r.created, r.modified, r.has_viewed, r.status,
                r.extra_guests, r.comment, r.event_id, g.new_id
            FROM seevooplay_reply r
            JOIN seevooplay_guest g ON g.id = r.guest_id
        """)

        # drop old tables
        cursor.execute("DROP TABLE seevooplay_reply")
        cursor.execute("DROP TABLE seevooplay_guest")

        # rename new tables
        cursor.execute("ALTER TABLE new__seevooplay_guest RENAME TO seevooplay_guest")
        cursor.execute("ALTER TABLE new__seevooplay_reply RENAME TO seevooplay_reply")

        # re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")


def forwards(apps, schema_editor):
    # only SQLite needs manual help; other db's will use the AlterField below
    if schema_editor.connection.vendor == 'sqlite':
        swap_pk_sqlite(apps, schema_editor)


class Migration(migrations.Migration):

    dependencies = [
        ("seevooplay", "0003_copy_uuid_and_assign_new_ids"),
    ]

    operations = [
        # run the manual SQLite PK swap (no-op for other databases)
        migrations.RunPython(forwards, migrations.RunPython.noop),

        # update Django's migration state to reflect the new schema
        # for SQLite: this just updates state without touching the DB
        # for other db's: Django will execute these operations normally
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql=migrations.RunSQL.noop,
            state_operations=[
                migrations.RemoveField(model_name="guest", name="new_id"),
                migrations.AlterField(
                    model_name="guest",
                    name="id",
                    field=models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
            ],
        ),
    ]
