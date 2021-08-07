from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import get_template


def get_event_info_block(event):
    # TODO
    pass


def send_guest_emails():
    """
    TODO
    build me now, ya shite
    """


def send_invitations(request, event, from_email, guest_list):
    """
    Send invitation emails, based on seevooplay/invitation_email.txt.
    """
    subject = f'event invitation: {event.name}'
    template = get_template('seevooplay/invitation_email.txt')
    for guest in guest_list:
        context = {
            'event': event,
            'guest': guest,
            'guest_id': str(guest.id),
            'host': request.get_host(),
            'protocol': request.META['wsgi.url_scheme'],
        }
        message = template.render(context)
        send_mail(subject, message, from_email, (guest.email,))
    recipients = ', '.join([g.email for g in guest_list])
    messages.add_message(request, messages.INFO, f'Email sent to: {recipients}')
