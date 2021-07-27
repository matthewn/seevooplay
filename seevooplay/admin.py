from django.contrib import admin

from .models import (
    Event,
    Guest,
    Reply,
)


class StatusesInline(admin.TabularInline):
    """
    We use this inline to show invitees and their responses
    on EventAdmin pages.
    """
    model = Reply
    extra = 0
    verbose_name_plural = 'Invitees & Responses'

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = (
        ('name', 'host'),
        'start_datetime',
        'end_datetime',
        ('location_name', 'location_address'),
        'details',
        'image',
        'invitees',
    )
    inlines = (StatusesInline,)
    list_display = ('__str__', 'created', 'modified')

    class Media:
        css = {'all': ('seevooplay/css/seevooplay.css',)}

    def save_model(self, request, obj, form, change):
        """
        Do some things with the raw data in the 'invitees' field.

        (1) Convert the raw guestlist from 'invitees' into Guest objects.
        (2) Email the invite to guests who haven't been invited to this event.
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
            name = ' '.join(words[:-1])
            # TODO this needs to be wrapped in a try/catch
            guest = Guest.objects.get_or_create(email=email)[0]
            guest.name = name or email
            guest.save()
            all_guests.append(guest)
        new_guests = []
        for guest in all_guests:
            if guest not in obj.guests.all():
                new_guests.append(guest)
        # TODO EMAIL NEW GUESTS HERE
        super().save_model(request, obj, form, change)
        obj.guests.set(all_guests)


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    inlines = (StatusesInline,)
    list_display = ('__str__', 'created', 'modified')
    readonly_fields = ('email',)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    """
    For testing purposes only!
    """
    list_display = ('__str__', 'created', 'modified')
