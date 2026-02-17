from django.urls import reverse

import re


def test_event_page(event, guest1, client):
    url = reverse('event_page', args=[event.id, guest1.short_uuid])
    response = client.get(url)
    assert response.status_code == 200
    assert 'No Reply: 2' in response.content.decode()


def test_event_page_admin_access(event, admin_client):
    url = reverse('invitation', args=[event.id])
    response = admin_client.get(url)
    assert response.status_code == 200
    assert 'No Reply: 2' in response.content.decode()


def test_event_page_no_snooping(event, client):
    url = reverse('invitation', args=[event.id])
    response = client.get(url)
    assert response.status_code == 403


def test_event_page_reply_yes(event, guest1, client, mailoutbox):
    url = reverse('event_page', args=[event.id, guest1.short_uuid])
    response = client.post(
        url,
        {
            'status': 'Y',
            'extra_guests': '1',
            'comment': 'WOOOO!',
        },
    )
    assert response.status_code == 200
    html = response.content.decode()
    assert 'Thank you for your reply!' in html
    assert 'Yes: 2' in html
    assert 'No Reply: 1' in html
    assert '<div class="comment">WOOOO!</div>' in html
    assert len(mailoutbox) == 1


def test_event_page_reply_no(event, guest1, client, mailoutbox):
    url = reverse('event_page', args=[event.id, guest1.short_uuid])
    response = client.post(
        url,
        {
            'status': 'N',
            'extra_guests': '0',
        },
    )
    assert response.status_code == 200
    html = response.content.decode()
    assert 'We will miss you!' in html
    assert 'No: 1' in html
    assert 'No Reply: 1' in html
    assert len(mailoutbox) == 1


def test_event_page_reply_maybe(event, guest1, client, mailoutbox):
    url = reverse('event_page', args=[event.id, guest1.short_uuid])
    response = client.post(
        url,
        {
            'status': 'M',
            'extra_guests': '3',
        },
    )
    assert response.status_code == 200
    html = response.content.decode()
    assert 'We hope you can make it!' in html
    assert 'Maybe: 4' in html
    assert 'No Reply: 1' in html
    assert len(mailoutbox) == 1


def test_resend_emails(event, guest1, client, mailoutbox):
    response = client.post(reverse('resend_page'), {'email': 'guest1@example.org'})
    assert len(mailoutbox) == 1
    assert (
        'Hey there, Guest One! There&#x27;s email headed your way.'
        in response.content.decode()
    )


def test_resend_emails_unknown(event, client, mailoutbox):
    response = client.post(reverse('resend_page'), {'email': 'foo@example.org'})
    assert len(mailoutbox) == 0
    assert (
        'Sorry, foo@example.org is not in our records'
        in response.content.decode()
    )


def test_resend_emails_past_event(past_event, guest1, client, mailoutbox):
    response = client.post(reverse('resend_page'), {'email': 'guest1@example.org'})
    assert len(mailoutbox) == 0
    assert (
        'Sorry, no outstanding invites for you, Guest One.'
        in response.content.decode()
    )


def process_test_email_response(response, admin_client):
    """
    Helper function for the next four tests.
    """
    assert response.status_code == 302  # redirect after successful save
    response = admin_client.get(response.url)  # fetch content of page we got redirected to
    pattern = r'<li class="info">Email sent to:\s*([^<]+)</li>'
    match = re.search(pattern, response.content.decode())
    email_display_count = 0
    if match:
        email_list = match.group(1)
        email_display_count = len([email.strip() for email in email_list.split(',') if email.strip()])
        return email_display_count


def test_email_guests_1(big_event, admin_client, mailoutbox):
    url = reverse('admin:seevooplay_email_guests', args=[big_event.id])
    response = admin_client.post(
        url,
        {
            'want_reply_yes': ['on'],
            'want_reply_maybe': ['on'],
            'want_reply_no': ['on'],
            'want_reply_none': ['on'],
            'want_have_viewed': ['on'],
            'want_have_not_viewed': ['on'],
            'subject': ['foo'],
            'message': ['bar'],
        },
    )
    email_display_count = process_test_email_response(response, admin_client)
    assert email_display_count == 12
    assert len(mailoutbox) == 12


def test_email_guests_2(big_event, admin_client, mailoutbox):
    url = reverse('admin:seevooplay_email_guests', args=[big_event.id])
    response = admin_client.post(
        url,
        {
            'want_reply_maybe': ['on'],
            'want_reply_no': ['on'],
            'want_reply_none': ['on'],
            'want_have_viewed': ['on'],
            'want_have_not_viewed': ['on'],
            'subject': ['foo'],
            'message': ['bar'],
        },
    )
    email_display_count = process_test_email_response(response, admin_client)
    assert email_display_count == 8
    assert len(mailoutbox) == 8


def test_email_guests_3(big_event, admin_client, mailoutbox):
    url = reverse('admin:seevooplay_email_guests', args=[big_event.id])
    response = admin_client.post(
        url,
        {
            'want_reply_none': ['on'],
            'want_have_not_viewed': ['on'],
            'subject': ['foo'],
            'message': ['bar'],
        },
    )
    email_display_count = process_test_email_response(response, admin_client)
    assert email_display_count == 2
    assert len(mailoutbox) == 2


def test_email_guests_4(big_event, admin_client, mailoutbox):
    url = reverse('admin:seevooplay_email_guests', args=[big_event.id])
    response = admin_client.post(
        url,
        {
            'want_reply_yes': ['on'],
            'want_reply_maybe': ['on'],
            'want_reply_no': ['on'],
            'want_reply_none': ['on'],
            'want_have_viewed': ['on'],
            'subject': ['foo'],
            'message': ['bar'],
        },
    )
    email_display_count = process_test_email_response(response, admin_client)
    assert email_display_count == 10
    assert len(mailoutbox) == 10
