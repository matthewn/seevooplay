from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.formats import date_format, time_format

import pytz

from .forms import EmailGuestsForm, ReplyForm
from .models import Event, Guest, Reply
from .utils import send_guest_emails, send_reply_notifications

TZ = pytz.timezone(settings.TIME_ZONE)


def event_page(request, event_id, guest_uuid=None):
    """
    Function-based view that drives the page our guests interact with.
    """
    event = Event.objects.get(id=event_id)

    start_datetime = event.start_datetime.astimezone(tz=TZ)
    end_datetime = event.end_datetime.astimezone(tz=TZ) if event.end_datetime else None
    if end_datetime and start_datetime.date() == end_datetime.date():
        date_display = f"{date_format(start_datetime.date())} {time_format(start_datetime.time())} – {time_format(end_datetime.time())}"
    elif end_datetime:
        date_display = f'{date_format(start_datetime)} {time_format(start_datetime)} – {date_format(end_datetime)} {time_format(end_datetime)}'
    else:
        date_display = f'{date_format(start_datetime)} {time_format(start_datetime)}'

    if guest_uuid is None:
        if not request.user.is_staff:
            raise PermissionDenied
        else:
            guest = None
    else:
        guest = Guest.objects.get(id=guest_uuid)

    if guest:
        guest_reply = Reply.objects.get(event=event, guest=guest)
        guest_reply.has_viewed = True
        # we save() no matter what so we can use the 'modified' field
        # to tell us when they last viewed the page
        guest_reply.save()

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid() and guest:
            guest_reply.status = form.cleaned_data['status']
            guest_reply.extra_guests = form.cleaned_data['extra_guests']
            guest_reply.comment = form.cleaned_data['comment']
            guest_reply.save()

            # send reply_notification_email
            address_list = [event.host1_email]
            if event.host2_email:
                address_list.append(event.host2_email)
            send_reply_notifications(request, guest_reply, None, address_list)

            messages.add_message(request, messages.INFO, 'Thank you for your reply!')
            if guest_reply.status == 'Y':
                messages.add_message(request, messages.INFO, 'We look forward to seeing you!')
            if guest_reply.status == 'M':
                messages.add_message(request, messages.INFO, 'We hope you can make it!')
            if guest_reply.status == 'N':
                messages.add_message(request, messages.INFO, 'We will miss you!')
    else:
        if guest:
            form = ReplyForm(
                initial={
                    'status': guest_reply.status,
                    'extra_guests': guest_reply.extra_guests,
                    'comment': guest_reply.comment,
                }
            )
        else:
            form = ReplyForm()

    replies = Reply.objects.filter(event=event)

    yes_replies = replies.filter(status='Y')
    maybe_replies = replies.filter(status='M')
    no_replies = replies.filter(status='N')
    none_replies = replies.filter(status='')

    yes_replies_count = yes_replies.count()
    if yes_replies.aggregate(Sum('extra_guests'))['extra_guests__sum']:
        yes_replies_count += yes_replies.aggregate(
            Sum('extra_guests')
        )['extra_guests__sum']

    maybe_replies_count = maybe_replies.count()
    if maybe_replies.aggregate(Sum('extra_guests'))['extra_guests__sum']:
        maybe_replies_count += maybe_replies.aggregate(
            Sum('extra_guests')
        )['extra_guests__sum']

    return TemplateResponse(
        request,
        'seevooplay/event.html',
        {
            'event': event,
            'form': form,
            'guest': guest,
            'yes_replies': yes_replies,
            'maybe_replies': maybe_replies,
            'no_replies': no_replies,
            'none_replies': none_replies,
            'yes_replies_count': yes_replies_count,
            'maybe_replies_count': maybe_replies_count,
            'date_display': date_display,
        },
    )


@staff_member_required
def email_guests(request, event_id):
    """
    Function-based view that drives an admin page for emailing our guests.
    """
    event = Event.objects.get(id=event_id)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request
        form = EmailGuestsForm(request.POST)
        if form.is_valid():
            recipients = []

            if form.cleaned_data['want_reply_yes']:
                replies = Reply.objects.filter(event=event, status='Y')
                recipients.append([reply.guest for reply in replies])

            if form.cleaned_data['want_reply_no']:
                replies = Reply.objects.filter(event=event, status='N')
                recipients.append([reply.guest for reply in replies])

            if form.cleaned_data['want_reply_maybe']:
                replies = Reply.objects.filter(event=event, status='M')
                recipients.append([reply.guest for reply in replies])

            if form.cleaned_data['want_reply_none']:
                replies = Reply.objects.filter(event=event, status='')
                recipients.append([reply.guest for reply in replies])

            recipients = [  # flatten the list-of-lists
                item for sublist in recipients for item in sublist
            ]
            recipients = set(recipients)

            if form.cleaned_data['want_have_viewed']:
                replies = Reply.objects.filter(event=event, has_viewed=True)
                have_viewed = set([reply.guest for reply in replies])

            if form.cleaned_data['want_have_not_viewed']:
                replies = Reply.objects.filter(event=event, has_viewed=False)
                have_not_viewed = set([reply.guest for reply in replies])

            # time for some set operations!
            if 'have_viewed' in locals() and 'have_not_viewed' in locals():
                group_1 = recipients.intersection(have_viewed)
                group_2 = recipients.intersection(have_not_viewed)
                recipients = group_1.union(group_2)
            elif 'have_viewed' in locals():
                recipients = recipients.intersection(have_viewed)
            elif 'have_not_viewed' in locals():
                recipients = recipients.intersection(have_not_viewed)

            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            send_guest_emails(request, event, subject, message, None, recipients)

            return HttpResponseRedirect(
                reverse('admin:seevooplay_event_change', args=(event_id,))
            )

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EmailGuestsForm()

    return TemplateResponse(
        request,
        'seevooplay/email_guests.html',
        {
            'event': event,
            'form': form,
        }
    )
