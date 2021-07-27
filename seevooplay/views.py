from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .forms import EmailGuestsForm
from .models import Event, Reply


@staff_member_required
def email_guests(request, event_id):
    event = Event.objects.get(id=event_id)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request
        form = EmailGuestsForm(request.POST)
        if form.is_valid():
            people_to_email = []

            if form.cleaned_data['want_reply_yes']:
                replies = Reply.objects.filter(event=event, status='Y')
                people_to_email.append([reply.guest for reply in replies])

            if form.cleaned_data['want_reply_no']:
                replies = Reply.objects.filter(event=event, status='N')
                people_to_email.append([reply.guest for reply in replies])

            if form.cleaned_data['want_reply_maybe']:
                replies = Reply.objects.filter(event=event, status='M')
                people_to_email.append([reply.guest for reply in replies])

            if form.cleaned_data['want_reply_none']:
                replies = Reply.objects.filter(event=event, status='')
                people_to_email.append([reply.guest for reply in replies])

            people_to_email = [  # flatten the list-of-lists
                item for sublist in people_to_email for item in sublist
            ]
            people_to_email = set(people_to_email)

            if form.cleaned_data['want_have_viewed']:
                replies = Reply.objects.filter(event=event, has_viewed=True)
                have_viewed = set([reply.guest for reply in replies])

            if form.cleaned_data['want_have_not_viewed']:
                replies = Reply.objects.filter(event=event, has_viewed=False)
                have_not_viewed = set([reply.guest for reply in replies])

            # time for some set operations!
            if 'have_viewed' in locals() and 'have_not_viewed' in locals():
                group_1 = people_to_email.intersection(have_viewed)
                group_2 = people_to_email.intersection(have_not_viewed)
                people_to_email = group_1.union(group_2)
            elif 'have_viewed' in locals():
                people_to_email = people_to_email.intersection(have_viewed)
            elif 'have_not_viewed' in locals():
                people_to_email = people_to_email.intersection(have_not_viewed)

            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # TODO: SEND THE MESSAGES HERE

            messages.add_message(
                request,
                messages.INFO,
                f'event id: {event}, subject: {subject}, message: {message}',
            )
            messages.add_message(
                request,
                messages.INFO,
                f'people to email: {people_to_email}',
            )
            return HttpResponseRedirect(
                reverse('admin:seevooplay_event_change', args=(event_id,))
            )

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EmailGuestsForm()

    return render(
        request,
        'seevooplay/email_guests.html',
        {
            'event': event,
            'form': form,
        }
    )
