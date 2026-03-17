from bs4 import BeautifulSoup
from types import SimpleNamespace
from django.urls import reverse
from seevooplay.admin import EventAdmin
from seevooplay.models import Guest


def test_process_invitees_empty_line(db):
    # ensure empty line in invitees doesn't generate anything
    obj = SimpleNamespace(invitees='prince@example.org,')
    all_guests = EventAdmin.process_invitees(None, [], obj)
    assert len(all_guests) == 1


def test_event_get_absolute_url(event):
    url = event.get_absolute_url()
    assert url == reverse('invitation', kwargs={'event_id': event.id})


def test_process_invitees(db):
    obj = SimpleNamespace(
        invitees='prince@example.org, madonna@example.org\r\n"Rip Torn" <rip_torn@example.org>\r\nTim Berners Lee tim@example.org'
    )

    all_guests = EventAdmin.process_invitees(None, [], obj)

    assert len(all_guests) == 4
    assert Guest.objects.count() == 4
    assert Guest.objects.filter(name='prince', email='prince@example.org').exists()
    assert Guest.objects.filter(name='madonna', email='madonna@example.org').exists()
    assert Guest.objects.filter(name='Rip Torn', email='rip_torn@example.org').exists()
    assert Guest.objects.filter(name='Tim Berners Lee', email='tim@example.org').exists()


def test_process_invitees_invalid_email(monkeypatch):
    def mock_add_message(req, level, msg):
        captured_messages.append(msg)

    monkeypatch.setattr('django.contrib.messages.add_message', mock_add_message)
    captured_messages = []
    obj = SimpleNamespace(invitees='prince@nowhere')

    all_guests = EventAdmin.process_invitees(None, [], obj)

    assert len(all_guests) == 0
    assert len(captured_messages) == 1
    assert captured_messages[0] == 'prince@nowhere is not a valid email address.'


def test_save_model_new(db, admin_client, mailoutbox):
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

    assert len(mailoutbox) == 2
    assert response.status_code == 302  # should redirect after successful save
    response = admin_client.get(response.url)  # fetch content of page we got redirected to
    assert 'was added successfully' in response.content.decode()
    assert 'New invitees added for My Event: larry, moe' in response.content.decode()
    assert Guest.objects.count() == 2


def get_admin_form_data(response):
    """Extract all form field values from a Django admin response."""
    soup = BeautifulSoup(response.content, 'html.parser')
    form_data = {}
    for field in soup.find_all(['input', 'select', 'textarea']):
        name = field.get('name')
        if not name:
            continue  # pragma: no cover (3 branches here not used in our forms)
        if field.name == 'input':
            if field.get('type') == 'checkbox':
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
    # GET the change form to get current field values
    response = admin_client.get(f'/admin/seevooplay/event/{event.pk}/change/')
    assert response.status_code == 200
    assert event.guests.all().count() == 2
    form_data = get_admin_form_data(response)

    # add to invitees field and submit
    existing_invitees = form_data.get('invitees', '')
    form_data['invitees'] = existing_invitees + '\r\nlarry@example.org'
    form_data['_save'] = 'Save'
    response = admin_client.post(
        f'/admin/seevooplay/event/{event.pk}/change/',
        form_data,
    )

    # check the results
    assert len(mailoutbox) == 1
    assert response.status_code == 302  # redirect after successful save
    response = admin_client.get(response.url)  # fetch content of page we got redirected to
    assert 'New invitees added for Fake Event: larry' in response.content.decode()
    larry = Guest.objects.get(name='larry')
    event.refresh_from_db()
    assert event.invitees.endswith('org\r\nlarry@example.org')
    assert event.guests.all().count() == 3
    assert guest1 in event.guests.all()
    assert guest2 in event.guests.all()
    assert larry in event.guests.all()
