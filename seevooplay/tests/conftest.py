import datetime as dt
import pytest
from zoneinfo import ZoneInfo

from seevooplay.models import Event, Guest, Reply


NUMBERS = [
    'One', 'Two', 'Three', 'Four', 'Five', 'Six',
    'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve'
]


def create_guest_fixture(n):
    @pytest.fixture
    def guest_fixture(db):
        guest = Guest.objects.create(
            name=f'Guest {NUMBERS[n - 1]}',
            email=f'guest{n}@example.org'
        )
        yield guest
        guest.delete()
    return guest_fixture


# make guest1 through guest12 available to all tests
for i in range(1, 13):
    globals()[f'guest{i}'] = create_guest_fixture(i)


def make_event(guests, **kwargs):
    """Factory helper for creating Event instances with sensible defaults."""
    defaults = {
        'name': 'Fake Event',
        'host1_name': 'Groovy',
        'host1_email': 'groovy@example.org',
        'start_datetime': dt.datetime(2030, 1, 1, 12, tzinfo=ZoneInfo('America/Los_Angeles')),
        'location_name': 'Fake Location',
    }
    defaults.update(kwargs)
    event = Event.objects.create(**defaults)
    if guests:
        event.guests.add(*guests)
        Reply.objects.filter(event=event).update(invitation_sent=True)
    return event


@pytest.fixture
def event(db, guest1, guest2):
    event = make_event(
        [guest1, guest2],
        invitees='Guest One guest1@example.org, Guest Two guest2@example.org',
    )
    yield event
    Reply.objects.filter(event=event).delete()
    event.delete()


@pytest.fixture
def past_event(db, guest1, guest2):
    event = make_event(
        [guest1, guest2],
        name='Past Event',
        invitees='Guest One guest1@example.org, Guest Two guest2@example.org',
        start_datetime=dt.datetime(2020, 1, 1, 12, tzinfo=ZoneInfo('America/Los_Angeles')),
    )
    yield event
    Reply.objects.filter(event=event).delete()
    event.delete()


@pytest.fixture
def same_day_event(db, guest1):
    event = make_event(
        [guest1],
        name='Same Day Event',
        end_datetime=dt.datetime(2030, 1, 1, 15, tzinfo=ZoneInfo('America/Los_Angeles')),
    )
    yield event
    Reply.objects.filter(event=event).delete()
    event.delete()


@pytest.fixture
def multiday_event(db, guest1):
    event = make_event(
        [guest1],
        name='Multi Day Event',
        end_datetime=dt.datetime(2030, 1, 2, 15, tzinfo=ZoneInfo('America/Los_Angeles')),
    )
    yield event
    Reply.objects.filter(event=event).delete()
    event.delete()


@pytest.fixture
def two_host_event(db, guest1):
    event = make_event(
        [guest1],
        name='Two Host Event',
        host2_name='Spirit',
        host2_email='spirit@example.org',
    )
    yield event
    Reply.objects.filter(event=event).delete()
    event.delete()


@pytest.fixture
def big_event(
    event,
    guest1, guest2, guest3, guest4, guest5, guest6,
    guest7, guest8, guest9, guest10, guest11, guest12,
):
    # guests 1 and 2 are built-in to event; we add the rest here
    # (adding guests creates Reply objects)
    event.guests.add(
        guest3, guest4, guest5, guest6, guest7, guest8,
        guest9, guest10, guest11, guest12
    )
    Reply.objects.filter(event=event).update(invitation_sent=True)
    # set some varying replies
    reply_guest1 = Reply.objects.get(guest=guest1)
    reply_guest1.status = 'Y'
    reply_guest1.has_viewed = True
    reply_guest1.save()
    reply_guest2 = Reply.objects.get(guest=guest2)
    reply_guest2.status = 'Y'
    reply_guest2.has_viewed = True
    reply_guest2.save()
    reply_guest3 = Reply.objects.get(guest=guest3)
    reply_guest3.status = 'Y'
    reply_guest3.has_viewed = True
    reply_guest3.save()
    reply_guest4 = Reply.objects.get(guest=guest4)
    reply_guest4.status = 'Y'
    reply_guest4.has_viewed = True
    reply_guest4.save()
    reply_guest5 = Reply.objects.get(guest=guest5)
    reply_guest5.status = 'M'
    reply_guest5.has_viewed = True
    reply_guest5.save()
    reply_guest6 = Reply.objects.get(guest=guest6)
    reply_guest6.status = 'M'
    reply_guest6.has_viewed = True
    reply_guest6.save()
    reply_guest7 = Reply.objects.get(guest=guest7)
    reply_guest7.status = 'M'
    reply_guest7.has_viewed = True
    reply_guest7.save()
    reply_guest8 = Reply.objects.get(guest=guest8)
    reply_guest8.status = 'N'
    reply_guest8.has_viewed = True
    reply_guest8.save()
    reply_guest9 = Reply.objects.get(guest=guest9)
    reply_guest9.status = 'N'
    reply_guest9.has_viewed = True
    reply_guest9.save()
    # guest10 has viewed, but not replied
    reply_guest10 = Reply.objects.get(guest=guest10)
    reply_guest10.has_viewed = True
    reply_guest10.save()
    # guests 11 and 12 have not viewed, not replied
    return event
    # cleanup is handled by parent fixtures
