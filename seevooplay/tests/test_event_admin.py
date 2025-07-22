from types import SimpleNamespace

from seevooplay.models import Guest
from seevooplay.admin import EventAdmin

# import pytest


def test_process_invitees(db):
    obj = SimpleNamespace(
        invitees='prince@example.org, madonna@example.org\r\n"Rip Torn" <rip_torn@example.org>\r\nTim Berners Lee tim@example.org'
    )

    all_guests = EventAdmin.process_invitees(None, [], obj)

    assert len(all_guests) == 4
    assert Guest.objects.count() == 4
    assert Guest.objects.filter(name='prince').exists()
    assert Guest.objects.filter(name='madonna').exists()
    assert Guest.objects.filter(name='Rip Torn').exists()
    assert Guest.objects.filter(name='Tim Berners Lee').exists()
    assert Guest.objects.filter(email='prince@example.org').exists()
    assert Guest.objects.filter(email='madonna@example.org').exists()
    assert Guest.objects.filter(email='rip_torn@example.org').exists()
    assert Guest.objects.filter(email='tim@example.org').exists()


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


def test_save_model(db, admin_client, monkeypatch):
    def mock_send_invitations(request, obj, from_email, guest_list):
        assert len(guest_list) == 2

    monkeypatch.setattr('seevooplay.admin.send_invitations', mock_send_invitations)

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

    assert response.status_code == 302  # should redirect after successful save
    response = admin_client.get(response.url)  # fetch content of page we got redirected to
    assert 'was added successfully' in response.content.decode()
    assert 'New invitees added for My Event: larry, moe' in response.content.decode()
    assert Guest.objects.count() == 2
