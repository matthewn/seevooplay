import datetime
from urllib.parse import unquote
from zoneinfo import ZoneInfo

from seevooplay.templatetags.add_to_calendar import _generate_calendar_links

TZ = ZoneInfo('America/Los_Angeles')
START = datetime.datetime(2030, 6, 15, 18, 0, 0, tzinfo=TZ)
END = datetime.datetime(2030, 6, 15, 21, 0, 0, tzinfo=TZ)


def test_non_datetime_start_returns_empty():
    result = _generate_calendar_links('Party', 'not a datetime', END, 'Home', 'https', 'example.com', '/rsvp/1/')
    assert result == {}


def test_returns_all_calendar_keys():
    result = _generate_calendar_links('Party', START, END, 'Home', 'https', 'example.com', '/rsvp/1/')
    assert set(result.keys()) == {'google', 'yahoo', 'outlook_365', 'ics'}


def test_none_end_datetime_uses_start():
    result = _generate_calendar_links('Party', START, None, 'Home', 'https', 'example.com', '/rsvp/1/')
    start_str = START.strftime('%Y%m%dT%H%M%SZ')
    assert f'dates={start_str}/{start_str}' in result['google']


def test_non_datetime_end_uses_start():
    result = _generate_calendar_links('Party', START, 'not a datetime', 'Home', 'https', 'example.com', '/rsvp/1/')
    start_str = START.strftime('%Y%m%dT%H%M%SZ')
    assert f'dates={start_str}/{start_str}' in result['google']


def test_with_url_includes_description():
    result = _generate_calendar_links('Party', START, END, 'Home', 'https', 'example.com', '/rsvp/1/')
    ics_decoded = unquote(result['ics'])
    assert 'DESCRIPTION:More info: https://example.com/rsvp/1/' in ics_decoded


def test_without_url_no_description():
    result = _generate_calendar_links('Party', START, END, 'Home', '', '', '')
    ics_decoded = unquote(result['ics'])
    assert 'DESCRIPTION:\n' in ics_decoded or 'DESCRIPTION:END' in ics_decoded or 'DESCRIPTION:\r' in ics_decoded


def test_ics_is_data_uri():
    result = _generate_calendar_links('Party', START, END, 'Home', 'https', 'example.com', '/rsvp/1/')
    assert result['ics'].startswith('data:text/calendar;charset=utf8,')


def test_ics_contains_vcalendar_structure():
    result = _generate_calendar_links('Party', START, END, 'Home', 'https', 'example.com', '/rsvp/1/')
    ics_decoded = unquote(result['ics'])
    assert 'BEGIN:VCALENDAR' in ics_decoded
    assert 'BEGIN:VEVENT' in ics_decoded
    assert 'END:VEVENT' in ics_decoded
    assert 'SUMMARY:Party' in ics_decoded
