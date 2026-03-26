from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.urls import path, reverse
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
        ('location_name', 'location_address'),
        'start_datetime',
        'end_datetime',
        ('details', 'image'),
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
        Process 'invitees' field on save.
        """
        all_guests = self.process_invitees(request, obj)
        super().save_model(request, obj, form, change)
        obj.guests.set(all_guests)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and request.method == 'POST' and '_send_invitations' in request.POST:
            # 'Send invitations' has been clicked
            pending = obj.reply_set.filter(invitation_sent=False).select_related('guest')
            send_invitations(request, obj, None, [r.guest for r in pending])
            return HttpResponseRedirect(
                reverse('admin:seevooplay_event_change', args=(object_id,))
            )

        extra_context = extra_context or {}
        if obj:
            extra_context['pending_replies'] = obj.reply_set.filter(
                invitation_sent=False
            ).select_related('guest')

        return super().change_view(request, object_id, form_url, extra_context)

    def _pending_invitations_redirect(self, obj):
        """
        Return a redirect to the change form if there are unsent invitations, else None.
        """
        if obj.reply_set.filter(invitation_sent=False).exists():
            return HttpResponseRedirect(
                reverse('admin:seevooplay_event_change', args=(obj.pk,))
            )

    def response_post_save_add(self, request, obj):
        """
        Keep user on change form if there are unsent invitations.
        """
        return self._pending_invitations_redirect(obj) or super().response_post_save_add(request, obj)  # pragma: no cover

    def response_post_save_change(self, request, obj):
        """
        Keep user on change form if there are unsent invitations.
        """
        return self._pending_invitations_redirect(obj) or super().response_post_save_change(request, obj)


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
