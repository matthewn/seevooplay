from bs4 import BeautifulSoup
from types import SimpleNamespace
from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse
from seevooplay.admin import EventAdmin
from seevooplay.models import Event, Guest, Reply


def make_event_admin():
    return EventAdmin(model=Event, admin_site=AdminSite())


def make_request():
    request = RequestFactory().get('/')
    SessionMiddleware(lambda r: None).process_request(request)
    MessageMiddleware(lambda r: None).process_request(request)
    return request


def test_process_invitees_empty_line(db):
    # ensure empty line in invitees doesn't generate anything
    obj = SimpleNamespace(invitees='prince@example.org,')
    all_guests = make_event_admin().process_invitees(make_request(), obj)
    assert len(all_guests) == 1


def test_event_get_absolute_url(event):
    url = event.get_absolute_url()
    assert url == reverse('invitation', kwargs={'event_id': event.id})


def test_process_invitees(db):
    obj = SimpleNamespace(
        invitees='prince@example.org, madonna@example.org\r\n"Rip Torn" <rip_torn@example.org>\r\nTim Berners Lee tim@example.org'
    )

    all_guests = make_event_admin().process_invitees(make_request(), obj)

    assert len(all_guests) == 4
    assert Guest.objects.count() == 4
    assert Guest.objects.filter(name='prince', email='prince@example.org').exists()
    assert Guest.objects.filter(name='madonna', email='madonna@example.org').exists()
    assert Guest.objects.filter(name='Rip Torn', email='rip_torn@example.org').exists()
    assert Guest.objects.filter(name='Tim Berners Lee', email='tim@example.org').exists()


def test_process_invitees_invalid_email(db):
    obj = SimpleNamespace(invitees='prince@nowhere')
    request = make_request()

    all_guests = make_event_admin().process_invitees(request, obj)

    assert len(all_guests) == 0
    msgs = [m.message for m in get_messages(request)]
    assert len(msgs) == 1
    assert msgs[0] == 'prince@nowhere is not a valid email address.'


def test_save_model_new(db, admin_client, mailoutbox):
    # saving a new event with invitees redirects to the change form
    # with pending guests listed and no emails sent yet
    response = admin_client.post(
        '/admin/seevooplay/event/add/',
        {
            'name': 'My Event',
            'host1_name': 'Joe',
            'host1_email': 'joe@example.org',
            'start_datetime_0': '2029-01-01',
            'start_datetime_1': '18:00:00',
            'location_name': 'Our House',
            'invitees': 'larry@example.org, moe@example.org',
            '_save': 'Save',
            # req'd mgmt form data for the inline formset
            'reply_set-TOTAL_FORMS': '0',
            'reply_set-INITIAL_FORMS': '0',
        },
    )

    assert len(mailoutbox) == 0
    assert response.status_code == 302
    change_url = response.url
    assert '/change/' in change_url

    response = admin_client.get(change_url)
    assert response.status_code == 200
    content = response.content.decode()
    assert 'larry' in content
    assert 'moe' in content
    assert Guest.objects.count() == 2


def get_admin_form_data(response):
    """
    Extract all form field values from a Django admin response.
    """
    soup = BeautifulSoup(response.content, 'html.parser')
    form_data = {}
    for field in soup.find_all(['input', 'select', 'textarea']):
        name = field.get('name')
        if not name:
            continue  # pragma: no cover (3 branches here not used in our forms)
        if field.name == 'input':
            if field.get('type') == 'submit':
                continue
            elif field.get('type') == 'checkbox':
                form_data[name] = field.get('checked') is not None  # pragma: no cover
            else:
                form_data[name] = field.get('value', '')
        elif field.name == 'select':  # pragma: no cover
            selected = field.find('option', selected=True)
            form_data[name] = selected.get('value', '') if selected else ''
        elif field.name == 'textarea':
            form_data[name] = field.get_text()
    return form_data


def test_save_model_existing(db, admin_client, mailoutbox, event, guest1, guest2):
    # saving an existing event with a new invitee redirects to the change form
    # with the new guest listed as pending and no email sent yet
    response = admin_client.get(f'/admin/seevooplay/event/{event.pk}/change/')
    assert event.guests.all().count() == 2
    form_data = get_admin_form_data(response)

    form_data['invitees'] = form_data.get('invitees', '') + '\r\nlarry@example.org'
    form_data['_save'] = 'Save'
    response = admin_client.post(
        f'/admin/seevooplay/event/{event.pk}/change/',
        form_data,
    )

    assert len(mailoutbox) == 0
    assert response.status_code == 302
    assert '/change/' in response.url

    response = admin_client.get(response.url)
    assert 'larry' in response.content.decode()

    event.refresh_from_db()
    assert event.invitees.endswith('org\r\nlarry@example.org')
    assert event.guests.all().count() == 3
    assert guest1 in event.guests.all()
    assert guest2 in event.guests.all()
    assert Guest.objects.filter(name='larry').exists()


def test_send_invitations(db, admin_client, mailoutbox, event, guest1):
    # mark one guest's invitation as pending
    Reply.objects.filter(event=event, guest=guest1).update(invitation_sent=False)

    change_url = f'/admin/seevooplay/event/{event.pk}/change/'
    response = admin_client.post(change_url, {'_send_invitations': '1'})

    assert len(mailoutbox) == 1
    assert response.status_code == 302
    assert Reply.objects.get(event=event, guest=guest1).invitation_sent is True

    # re-saving when no invitations are pending goes to the changelist, not back here
    form_data = get_admin_form_data(admin_client.get(change_url))
    form_data['_save'] = 'Save'
    response = admin_client.post(change_url, form_data)
    assert response.url == '/admin/seevooplay/event/'
