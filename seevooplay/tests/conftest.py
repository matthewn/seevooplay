from zoneinfo import ZoneInfo
from seevooplay.models import Event, Guest

import datetime as dt
import pytest


@pytest.fixture
def guest1(db):
    guest1 = Guest.objects.create(name='Guest One', email='guest1@example.org')
    guest1.save()
    yield guest1
    guest1.delete()


@pytest.fixture
def guest2(db):
    guest2 = Guest.objects.create(name='Guest Two', email='guest2@example.org')
    guest2.save()
    yield guest2
    guest2.delete()


@pytest.fixture
def event(db, guest1, guest2):
    event = Event.objects.create(
        name='Fake Event',
        host1_name='Groovy',
        host1_email='groovy@example.org',
        invitees='Guest One guest1@example.org, Guest Two guest2@example.org',
        start_datetime=dt.datetime(
            2030, 1, 1, 12, tzinfo=ZoneInfo('America/Los_Angeles')
        ),
        location_name='Fake Location',
    )
    event.guests.add(guest1, guest2)
    event.save()
    yield event
    event.delete()
