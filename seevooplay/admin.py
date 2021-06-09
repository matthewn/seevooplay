from django.contrib import admin

from .models import Event, Guest, Reply


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = (
        ('name', 'host'),
        ('start_datetime', 'end_datetime'),
        ('location_name', 'location_address'),
        'details',
        'image',
        'invitees',
        'guests',
    )
    list_display = ('__str__', 'created', 'modified')
    readonly_fields = ('guests',)

    def save_model(self, request, obj, form, change):
        new_guests = []
        invitees = (
            obj.invitees.replace('"', '').replace('<', '').replace('>', '')
        )
        invitees = invitees.replace(',', '\r\n')
        lines = invitees.split('\r\n')
        for line in lines:
            words = line.split(' ')
            email = words[-1]
            name = ' '.join(words[:-1])
            guest = Guest.objects.get_or_create(email=email)[0]
            guest.name = name or email
            guest.save()
            new_guests.append(guest)
        super().save_model(request, obj, form, change)
        obj.guests.set(new_guests)


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created', 'modified')


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created', 'modified')
