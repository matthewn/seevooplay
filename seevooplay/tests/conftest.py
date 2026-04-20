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
        return Guest.objects.create(
            name=f'Guest {NUMBERS[n - 1]}',
            email=f'guest{n}@example.org'
        )
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
    return make_event(
        [guest1, guest2],
        invitees='Guest One guest1@example.org, Guest Two guest2@example.org',
    )


@pytest.fixture
def past_event(db, guest1, guest2):
    return make_event(
        [guest1, guest2],
        name='Past Event',
        invitees='Guest One guest1@example.org, Guest Two guest2@example.org',
        start_datetime=dt.datetime(2020, 1, 1, 12, tzinfo=ZoneInfo('America/Los_Angeles')),
    )


@pytest.fixture
def same_day_event(db, guest1):
    return make_event(
        [guest1],
        name='Same Day Event',
        end_datetime=dt.datetime(2030, 1, 1, 15, tzinfo=ZoneInfo('America/Los_Angeles')),
    )


@pytest.fixture
def multiday_event(db, guest1):
    return make_event(
        [guest1],
        name='Multi Day Event',
        end_datetime=dt.datetime(2030, 1, 2, 15, tzinfo=ZoneInfo('America/Los_Angeles')),
    )


@pytest.fixture
def two_host_event(db, guest1):
    return make_event(
        [guest1],
        name='Two Host Event',
        host2_name='Spirit',
        host2_email='spirit@example.org',
    )


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
    # set varying reply statuses and viewed flags
    # (guests 11 and 12 keep the defaults: no reply, not viewed)
    replies = Reply.objects.filter(event=event)
    replies.filter(guest__in=[guest1, guest2, guest3, guest4]).update(status='Y', has_viewed=True)
    replies.filter(guest__in=[guest5, guest6, guest7]).update(status='M', has_viewed=True)
    replies.filter(guest__in=[guest8, guest9]).update(status='N', has_viewed=True)
    replies.filter(guest=guest10).update(has_viewed=True)
    return event
