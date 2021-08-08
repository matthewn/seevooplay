from django.conf import settings
from django.db import models
from django.utils.html import mark_safe

from djrichtextfield.models import RichTextField
from model_utils.models import TimeStampedModel, UUIDModel

import pytz

TZ = pytz.timezone(settings.TIME_ZONE)


class Guest(TimeStampedModel, UUIDModel):
    name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} <{self.email}>'


class Event(TimeStampedModel):
    name = models.CharField(max_length=64)
    host1_name = models.CharField(max_length=128)
    host1_email = models.EmailField()
    host2_name = models.CharField(blank=True, max_length=128)
    host2_email = models.EmailField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)
    location_name = models.CharField(max_length=64)
    location_address = models.CharField(
        blank=True,
        max_length=128,
    )
    details = RichTextField(blank=True)
    image = models.ImageField(
        blank=True,
        upload_to='event_images/',
    )
    guests = models.ManyToManyField(
        Guest,
        blank=True,
        through='Reply',
        verbose_name='Invited guests'
    )
    invitees = models.TextField(
        blank=True,
        help_text=mark_safe('''
            Enter a list of email addresses separated by commas or new lines.
            <br>You can put full names before email addresses, and we'll try to
            figure the whole mess out.
            <br>Quotes and angle brackets will be ignored. Example input:
            <pre>    prince@example.org, madonna@example.org</pre>
            <pre>    "Rip Torn" &lt;rip_torn@example.org&gt;</pre>
            <pre>    Tim Berners Lee tim@example.org</pre>
            <big><b><i>New invitees will be immediately emailed!</b></i></big>
        ''')
    )

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
    has_viewed = models.BooleanField(default=False)
    status = models.CharField(
        blank=True,
        max_length=1,
        choices=ReplyStatus.choices,
    )
    extra_guests = models.PositiveSmallIntegerField(default=0)
    comment = models.CharField(
        blank=True,
        max_length=512,
    )

    class Meta:
        ordering = ('guest',)
        verbose_name_plural = 'Replies'

    def __str__(self):
        return f'{self.event.name}: {self.guest}: {self.status}'
