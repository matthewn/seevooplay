import datetime
from urllib.parse import unquote
from zoneinfo import ZoneInfo

from seevooplay.templatetags.add_to_calendar import (
    _generate_calendar_links,
    add_to_calendar,
    add_to_calendar_simple,
)

TZ = ZoneInfo('America/Los_Angeles')
START = datetime.datetime(2030, 6, 15, 18, 0, 0, tzinfo=TZ)
END = datetime.datetime(2030, 6, 15, 21, 0, 0, tzinfo=TZ)


def test_non_datetime_start_returns_empty():
    result = _generate_calendar_links('Party', 'not a datetime', END, 'Home', 'https', 'example.com', '/rsvp/1/')
    assert result == {}


def test_returns_all_calendar_keys():
    result = add_to_calendar_simple('Party', START, END, 'Home', 'https', 'example.com', '/rsvp/1/')
    assert set(result.keys()) == {'google', 'yahoo', 'outlook_365', 'ics'}


def test_none_end_datetime_uses_start():
    result = _generate_calendar_links('Party', START, None, 'Home', 'https', 'example.com', '/rsvp/1/')
    start_utc_str = START.astimezone(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    assert f'dates={start_utc_str}/{start_utc_str}' in result['google']


def test_non_datetime_end_uses_start():
    result = _generate_calendar_links('Party', START, 'not a datetime', 'Home', 'https', 'example.com', '/rsvp/1/')
    start_utc_str = START.astimezone(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    assert f'dates={start_utc_str}/{start_utc_str}' in result['google']


def test_with_url_includes_description():
    result = _generate_calendar_links('Party', START, END, 'Home', 'https', 'example.com', '/rsvp/1/')
    ics_decoded = unquote(result['ics'])
    assert 'DESCRIPTION:More info: https://example.com/rsvp/1/' in ics_decoded


def test_without_url_no_description():
    result = _generate_calendar_links('Party', START, END, 'Home', '', '', '')
    ics_decoded = unquote(result['ics'])
    lines = ics_decoded.splitlines()
    description_line = next(line for line in lines if line.startswith('DESCRIPTION:'))
    assert description_line == 'DESCRIPTION:'


def test_ics_is_data_uri():
    result = _generate_calendar_links('Party', START, END, 'Home', 'https', 'example.com', '/rsvp/1/')
    assert result['ics'].startswith('data:text/calendar;charset=utf8,')


def test_add_to_calendar_tag_invalid_start():
    result = add_to_calendar('Party', 'not a datetime')
    assert result == ''


def test_ics_contains_vcalendar_structure():
    result = _generate_calendar_links('Party', START, END, 'Home', 'https', 'example.com', '/rsvp/1/')
    ics_decoded = unquote(result['ics'])
    assert 'BEGIN:VCALENDAR' in ics_decoded
    assert 'BEGIN:VEVENT' in ics_decoded
    assert 'END:VEVENT' in ics_decoded
    assert 'SUMMARY:Party' in ics_decoded
