from django.contrib import messages
from django.core.mail import send_mass_mail


def get_event_info_block(event):
    # TODO
    pass


def send_emails(request, subject, message, from_email, recipient_list):
    datatuple = tuple(
        [
            (subject, message, from_email, (recipient.email,))
            for recipient in recipient_list
        ]
    )
    # TODO INCLUDE THE INFO BLOCK
    send_mass_mail(datatuple)
    recipients = ', '.join([g.email for g in recipient_list])
    messages.add_message(request, messages.INFO, f'Email sent to: {recipients}')
