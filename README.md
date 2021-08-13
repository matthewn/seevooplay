# Seevooplay

Seevooplay is a Django app for online invitations and RSVPs. Think of it as
your personal, selfhosted version of Evite (or a similar service.) Throwing a
party? Don't give all your friends' email addresses to Evite. Don't expect your
friends to be on Facebook. Kick the corporate middleman to the curb! Let
Seevooplay send email invitations and collect responses for you!

Seevooplay is intended for *personal* use and is not architected for scale. It
is directly inspired by [DaVite](http://marginalhacks.com/Hacks/DaVite/), a
2000-line Perl script from 2004 that was a very cool hack for its time, but is
inappropriate for use on the web in 2021. Seevooplay aims to solve the same
problems DaVite did, but with modern, maintainable, extensible code atop a
rock-solid foundation of Python and Django.

The "owner" of a Seevooplay instance interacts with Seevooplay mainly through
Django's admin. Invitees interact with a single public view, whose template and
styling is deliberately minimalistic and intended to be customized. Through
the magic of the CSS cascade and Django [template
overriding](https://docs.djangoproject.com/en/3.1/howto/overriding-templates/),
you can make what your guests see as gorgeous (or as ugly) as you like.

Your invitees will receive emails containing personalized links back to your
Seevooplay instance. They won't have to create an account to RSVP to your
event, because Seevooplay will already know who they are. *This does mean that
forwarded links are problematic: If Alice forwards her invitation to Bob, Bob
can RSVP as Alice.* In other words, from a security standpoint, Seevooplay is
about as naive as it gets. For the casual, personal use cases Seevooplay is
designed for, however, this model works. If it spooks you, your parties are
much higher stakes than mine, and you should look for a different solution. :)

Seevooplay is free software, licensed under the terms of the GNU General Public
License, Version 3. See the included COPYING file for complete details.

# Installation

Seevooplay can be integrated with existing Django projects, or run as a
standalone project.

## Standalone project

There is not (yet) a containerized distribution of Seevooplay, but if you are
familiar with Python, Django, and their modern ecosystems, you should have no
trouble getting Seevooplay up and running as a standalone Django project. In
broad strokes, the steps are:

1. Download the Seevooplay distribution and extract to a folder, or `git clone` it.
2. Copy config/settings/local.py.example to config/settings/local.py and edit local.py to match your server environment.
3. Create a Python virtual environment with your tool of choice and populate it with Seevooplay's dependencies. For example, `pip install -r requirements.txt` or `poetry install`.
4. From within your virtualenv:```
./manage.py migrate
./manage.py collectstatic
```
5. Use `./manage.py sendtestemail` to ensure your setup can send mail.
6. `./manage.py createsuperuser` to create a superuser.
7. Fire up the Django development server with `./manage.py runserver` or put your favorite server (gunicorn, nginx, apache) in front of the project.
8. In your browser, navigate to /admin and log in with your superuser credentials to poke around and create your first event in Seevooplay.

## Integrate with existing Django project

1. Add Seevooplay to your project with `pip install seevooplay` or `poetry add seevooplay` or whatever your Python package-manager-of-choice requires.
2. Add 'seevooplay' to INSTALLED_APPS in your settings.py.
3. Add settings for django-richtextfield in your settings.py. See FIXME TODO docs for details, or see example configuration in Seevooplay's config/settings.py.
4. Add the following lines to your urls.py: TODO FIXME

