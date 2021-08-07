from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import get_template


def send_guest_emails(request, event, subject, message, from_email, guest_list):
    """
    Send emails for the email_guests view.
    """
    template = get_template('seevooplay/email_guests_email.txt')
    for guest in guest_list:
        context = {
            'event': event,
            'guest': guest,
            'message': message,
            'host': request.get_host(),
            'protocol': request.META['wsgi.url_scheme'],
        }
        body = template.render(context)
        send_mail(subject, body, from_email, (guest.email,))
    recipients = ', '.join([g.email for g in guest_list])
    messages.add_message(request, messages.INFO, f'Email sent to: {recipients}')


def send_invitations(request, event, from_email, guest_list):
    """
    Send invitation emails.
    This is triggered by the save_model() method in EventAdmin.
    """
    subject = f'[invitation] {event.name}'
    template = get_template('seevooplay/invitation_email.txt')
    for guest in guest_list:
        context = {
            'event': event,
            'guest': guest,
            'host': request.get_host(),
            'protocol': request.META['wsgi.url_scheme'],
        }
        body = template.render(context)
        send_mail(subject, body, from_email, (guest.email,))
    recipients = ', '.join([g.email for g in guest_list])
    messages.add_message(request, messages.INFO, f'Email sent to: {recipients}')
