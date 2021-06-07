from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel


class Guest(TimeStampedModel, UUIDModel):
    name = models.CharField(max_length=64)
    email = models.EmailField()


class Event(TimeStampedModel):
    name = models.CharField(max_length=64)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True)
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
    image_height = models.PositiveIntegerField(blank=True)
    image_width = models.PositiveIntegerField(blank=True)
    guests = models.ManyToManyField(Guest, blank=True)


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

    class Meta:
        verbose_name_plural = 'replies'
