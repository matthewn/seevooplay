from django.contrib import admin

from .models import Event, Guest, Reply


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created', 'modified')


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created', 'modified')


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created', 'modified')
