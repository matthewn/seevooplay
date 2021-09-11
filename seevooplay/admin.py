from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import (
    Event,
    Guest,
    Reply,
)
from .utils import send_invitations


class StatusesInline(admin.TabularInline):
    """
    We use this inline to show invitees and their responses
    on EventAdmin pages.
    """
    model = Reply
    extra = 0
    verbose_name_plural = 'Invitations & Responses'

    class Media:
        css = {'all': ('seevooplay/css/admin.css',)}

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = (
        'name',
        ('host1_name', 'host1_email'),
        ('host2_name', 'host2_email'),
        ('start_datetime', 'end_datetime'),
        ('location_name', 'location_address'),
        'details',
        'image',
        'invitees',
    )
    inlines = (StatusesInline,)
    list_display = ('__str__', 'created', 'modified')

    def save_model(self, request, obj, form, change):
        """
        Do some things with the raw data in the 'invitees' field.

        (1) Convert the raw guestlist from 'invitees' into Guest objects.
        (2) Trigger email invitations for newly-added guests.
        """
        invitees = (
            obj.invitees.replace('"', '').replace('<', '').replace('>', '')
        )
        invitees = invitees.replace(',', '\r\n')
        lines = invitees.split('\r\n')
        all_guests = []
        for line in lines:
            words = line.split(' ')
            email = words[-1]
            if not email:
                continue
            try:
                validate_email(email)
                name = ' '.join(words[:-1])
                guest = Guest.objects.get_or_create(email=email)[0]
                guest.name = name or email
                guest.save()
                all_guests.append(guest)
            except ValidationError:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f'{email} is not a valid email address.',
                )
        new_guests = []
        for guest in all_guests:
            if obj._state.adding or guest not in obj.guests.all():
                new_guests.append(guest)

        super().save_model(request, obj, form, change)
        obj.guests.set(all_guests)

        if new_guests:
            new_guests_dsp = ', '.join([g.name for g in new_guests])
            messages.add_message(
                request,
                messages.INFO,
                f'New invitees added for {obj.name}: {new_guests_dsp}',
            )
            send_invitations(request, obj, None, new_guests)


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    inlines = (StatusesInline,)
    list_display = ('__str__', 'created', 'modified')
    readonly_fields = ('email',)


# @admin.register(Reply)
# class ReplyAdmin(admin.ModelAdmin):
#     """
#     For testing purposes only!
#     """
#     list_display = ('__str__', 'created', 'modified')
