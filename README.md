# Seevooplay

Seevooplay is a Django app for online invitations and RSVPs. Think of it as your personal, selfhosted version of Evite (or a similar service). Throwing a party? Don't give all your friends' email addresses to Evite. Don't expect your friends to be on Facebook. Embrace the indieweb, kick the corporate middleman to the curb, and let Seevooplay send email invitations and collect responses for you! That's the pitch, anyway.

Seevooplay was crafted for *personal* use; it is not architected for scale. It is directly inspired by [DaVite](http://marginalhacks.com/Hacks/DaVite/), a 2000-line Perl script last updated in 2004 -- a very cool and useful hack for its time, but inappropriate for use on the web in 2021. Seevooplay aims to solve the same problems DaVite did, in much the same way, but with modern, maintainable, extensible code, atop the rock-solid foundation of Python and Django.

The owner of a Seevooplay instance interacts with Seevooplay mainly through Django's admin. [[Screenshot 1](https://user-images.githubusercontent.com/782716/129496242-c791d261-0d5f-43a7-b65d-b8759685b9af.png), [Screenshot 2](https://user-images.githubusercontent.com/782716/129496271-2591b149-db9f-41bd-96ab-9cad18e91c08.png)] Invitees interact with a single public view, whose template and styling is deliberately minimalistic and intended to be customized. [[Screenshot 3](https://user-images.githubusercontent.com/782716/129496302-b2ebeff9-c73b-49cc-b971-706db8589f05.png)] Through the magic of the CSS cascade and Django [template overriding](https://docs.djangoproject.com/en/3.2/howto/overriding-templates/), you can make what your guests see as gorgeous (or as ugly) as you like.

Your invitees will receive emails containing personalized links back to your Seevooplay instance. They won't have to create any sort of account (or log in) to RSVP to your event; a UUID in their link tells Seevooplay who they are.  *This means that forwarded links are problematic: If Alice forwards her invitation to Bob, Bob can RSVP as Alice.* In other words, from a security standpoint, Seevooplay is about as naive as it gets. For the casual, personal use cases Seevooplay is designed for, however, this model works. If it spooks you, your parties are much higher stakes than mine, and you should look for a different solution. :)

Seevooplay is free software, licensed under the terms of the GNU General Public License, Version 3. See the included COPYING file for details.

# Installation

Seevooplay can be run as a standalone project, or integrated with an existing Django project.

## Run as a standalone project

There is not (yet) a containerized distribution of Seevooplay, but if you are familiar with Python, Django, and their modern ecosystems, you should have no trouble getting Seevooplay up and running as a standalone Django project. In broad strokes, the steps are:

1. Download the Seevooplay distribution and extract to a folder, or `git clone` it.
2. Copy config/settings/local.py.example to config/settings/local.py and edit local.py to match your server environment.
3. Create a Python virtual environment with your tool of choice and populate it with Seevooplay's dependencies. For example, `pip install -r requirements.txt` or `poetry install`.
4. The rest happens from within your virtualenv. First:
```
./manage.py migrate
./manage.py collectstatic
```
5. Do `./manage.py sendtestemail` to ensure your setup can send mail.
6. Do `./manage.py createsuperuser` to create a superuser.
7. Fire up the Django development server with `./manage.py runserver` or put your favorite server (gunicorn, nginx, apache) in front of the project.
8. In your browser, navigate to http://yourdomain/admin and log in with your superuser credentials to poke around and create your first event in Seevooplay. As long as you remain logged in, you can view your first event at http://yourdomain/rsvp/1.

## Integrate with an existing Django project

1. Add Seevooplay to your project with `pip install seevooplay` or `poetry add seevooplay` or whatever your Python package-manager-of-choice requires.
2. Add to INSTALLED_APPS in your settings.py:
```
'djrichtextfield',  # required for seevooplay
'seevooplay',
```
3. Add settings for django-richtextfield in your settings.py. See [django-richtextfield's docs](https://github.com/jaap3/django-richtextfield#django-rich-text-field) for details, or copy the DJRICHTEXTFIELD_CONFIG stanza from Seevooplay's config/settings/base.py.
4. In your main urls.py, add this import:
```
from seevooplay.views import email_guests, event_page
```
... and these urlpatterns:
```
path('admin/email_guests/<int:event_id>/', email_guests, name='email_guests'),
path('rsvp/<int:event_id>/', event_page, name='invitation'),
path('rsvp/<int:event_id>/<guest_uuid>/', event_page),
path('djrichtextfield/', include('djrichtextfield.urls')),
```
5. From within your project's virtual environment:
```
./manage.py migrate
./manage.py collectstatic
```
6. There should now be a Seevooplay section in your project's admin, where you can start kicking the tires.

# What Seevooplay Lacks

- 'Add to calendar' functionality. This is probably something I'll hack on at some point.
- Internationalization. I welcome pull requests to change this.
- HTML emails. Plain text emails don't bother me, so this is unlikely to change unless someone else does the work.
- Comprehensive documentation. If anyone other than me ends up using this, the docs will get better. In the meantime, if you try using Seevooplay and run into trouble, please open an issue on GitHub. I will help if I can.
- Perfection. This software was crafted to scratch a personal itch. It almost certainly has bugs. If you discover one, or you have a suggestion for improving the code, please open an issue on GitHub.
