from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save)
def process_raw_guests(sender, **kwargs):
    print('GOT IN!!!!!!!')
