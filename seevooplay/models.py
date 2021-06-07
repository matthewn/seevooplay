from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel

import pytz

TZ = pytz.timezone(settings.TIME_ZONE)


class Guest(TimeStampedModel, UUIDModel):
    name = models.CharField(max_length=64)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Event(TimeStampedModel):
    name = models.CharField(max_length=64)
    host = models.CharField(max_length=64)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)
    location_name = models.CharField(max_length=64)
    location_address = models.CharField(
        blank=True,
        max_length=128,
    )
    details = models.TextField(blank=True)
    image = models.ImageField(
        blank=True,
        upload_to='event_images/',
        height_field='image_height',
        width_field='image_width',
    )
    image_height = models.PositiveIntegerField(blank=True, null=True)
    image_width = models.PositiveIntegerField(blank=True, null=True)
    guests = models.ManyToManyField(Guest, blank=True)

    def __str__(self):
        return f'{self.name} ({self.start_datetime.astimezone(TZ).strftime("%x %I:%M %p %Z")})'


class ReplyStatus(models.TextChoices):
    YES = 'Y', 'Yes'
    NO = 'N', 'No'
    MAYBE = 'M', 'Maybe'


class Reply(TimeStampedModel):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
    )
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=1,
        choices=ReplyStatus.choices,
    )

    def __str__(self):
        return f'{self.event.name}: {self.guest}: {self.status}'

    class Meta:
        verbose_name_plural = 'replies'
