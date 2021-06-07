from django.contrib import admin

from .models import Event, Guest, Reply


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    pass


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    pass
