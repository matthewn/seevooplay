from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.urls import path
from django.utils.translation import gettext as _, gettext_lazy as _lazy

from .emails import send_invitations
from .models import (
    Event,
    Guest,
    Reply,
)
from .views import email_guests


class StatusesInline(admin.TabularInline):
    """
    We use this inline to show invitees and their responses
    on EventAdmin pages.
    """
    model = Reply
    extra = 0
    verbose_name_plural = _lazy('Invitations & Responses')

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

    def get_urls(self):
        """Add custom URL for emailing guests"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:event_id>/email-guests/',
                self.admin_site.admin_view(email_guests),
                name='seevooplay_email_guests',
            ),
        ]
        return custom_urls + urls

    def process_invitees(self, request, obj):
        """
        Convert a raw guestlist from the 'invitees' field into Guest objects.
        Returns a list of all the event's Guest objects.
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
                guest.name = name or email.split('@')[0]
                guest.save()
                all_guests.append(guest)
            except ValidationError:
                messages.add_message(
                    request,
                    messages.ERROR,
                    _('%(email)s is not a valid email address.') % {'email': email},
                )
        return all_guests

    def save_model(self, request, obj, form, change):
        """
        Process 'invitees' field and send email invitations to newly-added guests.
        """
        all_guests = self.process_invitees(request, obj)
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
                _('New invitees added for %(event_name)s: %(guest_names)s') % {
                    'event_name': obj.name,
                    'guest_names': new_guests_dsp,
                },
            )
            send_invitations(request, obj, None, new_guests)


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    inlines = (StatusesInline,)
    list_display = ('__str__', 'created', 'modified')
    readonly_fields = ('email', 'short_uuid', 'legacy_uuid')


# @admin.register(Reply)
# class ReplyAdmin(admin.ModelAdmin):
#     """
#     For testing purposes only!
#     """
#     list_display = ('__str__', 'created', 'modified')
