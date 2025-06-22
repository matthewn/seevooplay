from django import template
from django.utils.safestring import mark_safe
from urllib.parse import quote
import datetime

register = template.Library()


def _generate_calendar_links(start_datetime, end_datetime, title, location, scheme, host, url):
    """
    Internal function to generate calendar links for different services.
    Returns a dictionary with event-creating URLs for each calendar service.
    """
    if not isinstance(start_datetime, datetime.datetime):
        return {}

    # if no end_datetime provided, use start_datetime (creates a point-in-time event)
    if end_datetime is None or not isinstance(end_datetime, datetime.datetime):
        end_datetime = start_datetime

    title_encoded = quote(title)
    location_encoded = quote(location)
    url = scheme + '://' + host + url
    description = f'More info: {url}'
    description_encoded = quote(description)

    # format dates for Google/Yahoo (all use YYYYMMDDTHHMMSSZ format)
    start_str = start_datetime.strftime('%Y%m%dT%H%M%SZ')
    end_str = end_datetime.strftime('%Y%m%dT%H%M%SZ')

    # Outlook 365 uses ISO format dates (YYYY-MM-DDTHH:MM:SS.sssZ)
    start_outlook = start_datetime.isoformat() + 'Z'
    end_outlook = end_datetime.isoformat() + 'Z'

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
PRODID:-//Your Site//Add to Calendar//EN
BEGIN:VEVENT
UID:{start_datetime.strftime('%Y%m%d%H%M%S')}@yoursite.com
DTSTAMP:{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
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
def add_to_calendar(start_datetime, end_datetime, title, location, scheme, host, path):
    calendar_links = _generate_calendar_links(start_datetime, end_datetime, title, location, scheme, host, path)

    if not calendar_links:
        return ""

    html = f"""
    <div class="add-to-calendar">
        <div class="calendar-dropdown">
            <button class="calendar-btn" onclick="toggleCalendarDropdown(this)">
                📅 Add to Calendar
            </button>
            <div class="calendar-options" style="display: none;">
                <a href="{calendar_links['google']}" target="_blank" rel="noopener">Google Calendar</a>
                <a href="{calendar_links['outlook_365']}" target="_blank" rel="noopener">Outlook 365</a>
                <a href="{calendar_links['ics']}" download="event.ics">Apple Calendar</a>
                <a href="{calendar_links['ics']}" download="event.ics">Outlook (Desktop)</a>
                <a href="{calendar_links['yahoo']}" target="_blank" rel="noopener">Yahoo Calendar</a>
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
def add_to_calendar_simple(start_datetime, end_datetime, title, location, scheme, host, path):
    return _generate_calendar_links(start_datetime, end_datetime, title, location, scheme, host, path)
