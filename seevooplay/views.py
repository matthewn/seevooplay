from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .forms import EmailGuestsForm


@staff_member_required
def email_guests(request, event_id):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EmailGuestsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            messages.add_message(
                request,
                messages.INFO,
                'FOOOO!',
            )
            return HttpResponseRedirect(
                reverse('admin:seevooplay_event_change', args=(event_id,))
            )

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EmailGuestsForm()

    return render(request, 'seevooplay/email_guests.html', {'form': form})
