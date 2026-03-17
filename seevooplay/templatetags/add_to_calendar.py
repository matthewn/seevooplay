from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from urllib.parse import quote
import datetime

register = template.Library()


def _generate_calendar_links(title, start_datetime, end_datetime, location, scheme, host, path):
    if not isinstance(start_datetime, datetime.datetime):
        return {}

    # if no end_datetime provided, use start_datetime (creates a point-in-time event)
    if end_datetime is None or not isinstance(end_datetime, datetime.datetime):
        end_datetime = start_datetime

    title_encoded = quote(title)
    location_encoded = quote(location)
    url = f'{scheme}://{host}{path}' if scheme and host and path else ''
    description = f'More info: {url}' if url else ''
    description_encoded = quote(description)

    UTC = datetime.timezone.utc
    start_utc = start_datetime.astimezone(UTC) if start_datetime.tzinfo else start_datetime.replace(tzinfo=UTC)
    end_utc = end_datetime.astimezone(UTC) if end_datetime.tzinfo else end_datetime.replace(tzinfo=UTC)

    # format dates for Google/Yahoo/ICS (all use YYYYMMDDTHHMMSSZ format, UTC)
    start_str = start_utc.strftime('%Y%m%dT%H%M%SZ')
    end_str = end_utc.strftime('%Y%m%dT%H%M%SZ')

    # Outlook 365 uses ISO format dates (YYYY-MM-DDTHH:MM:SSZ, UTC)
    start_outlook = start_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_outlook = end_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    google_url = (
        f'https://calendar.google.com/calendar/render?'
        f'action=TEMPLATE&'
        f'text={title_encoded}&'
        f'dates={start_str}/{end_str}&'
        f'location={location_encoded}&'
        f'details={description_encoded}'
    )
    yahoo_url = (
        f'https://calendar.yahoo.com/?v=60&'
        f'title={title_encoded}&'
        f'st={start_str}&'
        f'et={end_str}&'
        f'in_loc={location_encoded}&'
        f'desc={description_encoded}'
    )
    outlook_url = (
        f'https://outlook.live.com/calendar/0/deeplink/compose?'
        f'subject={title_encoded}&'
        f'startdt={quote(start_outlook)}&'
        f'enddt={quote(end_outlook)}&'
        f'location={location_encoded}&'
        f'body={description_encoded}'
    )

    # generate ICS content for Apple/Outlook
    ics_description = description.replace('\n', '\\n')
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Seevooplay//Add to Calendar//EN
BEGIN:VEVENT
UID:{start_datetime.strftime('%Y%m%d%H%M%S')}@seevooplay
DTSTAMP:{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:{title}
LOCATION:{location}
DESCRIPTION:{ics_description}
END:VEVENT
END:VCALENDAR"""
    # create data URI for ICS file
    ics_data_uri = f'data:text/calendar;charset=utf8,{quote(ics_content)}'

    return {
        'google': google_url,
        'yahoo': yahoo_url,
        'outlook_365': outlook_url,
        'ics': ics_data_uri,
    }


@register.simple_tag
def add_to_calendar(title, start_datetime, end_datetime=None, location='', scheme='', host='', path=''):
    calendar_links = _generate_calendar_links(title, start_datetime, end_datetime, location, scheme, host, path)

    if not calendar_links:
        return ''

    add_to_calendar_label = _('Add to Calendar')
    google_label = _('Google Calendar')
    outlook_365_label = _('Outlook 365')
    apple_label = _('Apple Calendar')
    outlook_desktop_label = _('Outlook (Desktop)')
    yahoo_label = _('Yahoo Calendar')

    html = f"""
    <div class="add-to-calendar">
        <div class="calendar-dropdown">
            <button class="calendar-btn" onclick="toggleCalendarDropdown(this)">
                📅 {add_to_calendar_label}
            </button>
            <div class="calendar-options" style="display: none;">
                <a href="{calendar_links['google']}" target="_blank" rel="noopener">{google_label}</a>
                <a href="{calendar_links['outlook_365']}" target="_blank" rel="noopener">{outlook_365_label}</a>
                <a href="{calendar_links['ics']}" download="event.ics">{apple_label}</a>
                <a href="{calendar_links['ics']}" download="event.ics">{outlook_desktop_label}</a>
                <a href="{calendar_links['yahoo']}" target="_blank" rel="noopener">{yahoo_label}</a>
            </div>
        </div>
    </div>

    <script>
    function toggleCalendarDropdown(button) {{
        const dropdown = button.nextElementSibling;
        const isVisible = dropdown.style.display !== 'none';

        // hide all other dropdowns
        document.querySelectorAll('.calendar-options').forEach(d => d.style.display = 'none');

        // toggle current dropdown
        dropdown.style.display = isVisible ? 'none' : 'block';

        // close dropdown when clicking outside
        if (!isVisible) {{
            setTimeout(() => {{
                document.addEventListener('click', function closeDropdown(e) {{
                    if (!button.contains(e.target) && !dropdown.contains(e.target)) {{
                        dropdown.style.display = 'none';
                        document.removeEventListener('click', closeDropdown);
                    }}
                }});
            }}, 10);
        }}
    }}
    </script>
    """

    return mark_safe(html)


@register.simple_tag
def add_to_calendar_simple(title, start_datetime, end_datetime=None, location='', scheme='', host='', path=''):
    return _generate_calendar_links(title, start_datetime, end_datetime, location, scheme, host, path)
