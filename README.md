<h1 align="center">Seevooplay</h1>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0"><img src="https://img.shields.io/badge/license-GPL--3.0-blue" alt="License: GPL-3.0"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/django-5.2%2B-0C4B33" alt="Django 5.2+">
</p>

Seevooplay is a Django app for online invitations and RSVPs. **Think of it as your personal, self-hosted version of Partiful, Evite, Facebook Invitations, and the like.** Throwing a party? Don't give all your friends' phone numbers to Partiful, don't give their email addresses to Evite, don't expect them to be on Facebook. Embrace the indieweb, kick the corporate middleman to the curb, and let Seevooplay send email invitations and collect responses for you! That's the pitch, anyway.

Seevooplay is crafted for *personal* use; it is not architected for scale. It is directly inspired by [DaVite](http://marginalhacks.com/Hacks/DaVite/), a 2000-line Perl script last updated in 2004 -- a very cool and useful hack for its time, but wholly inappropriate for use on the modern web. Seevooplay aims to solve the same problems DaVite did, in much the same way, but with modern, maintainable, extensible code, atop the rock-solid foundation of Python and Django.

The owner of a Seevooplay instance interacts with Seevooplay mainly through Django's admin. Invitees generally interact with a single page, whose default template and styling is deliberately minimalistic and intended to be customized. Through the magic of the CSS cascade and Django [template overriding](https://docs.djangoproject.com/en/5.2/howto/overriding-templates/), you can make what your guests see as gorgeous (or as ugly) as you like.

<table><tr valign="top">
  <td><a href="https://github.com/user-attachments/assets/2bae3ea5-53d3-413a-b33a-1fadd4a1e6f6"><img src="https://github.com/user-attachments/assets/2bae3ea5-53d3-413a-b33a-1fadd4a1e6f6" alt="screenshot of admin view for editing an event" title="screenshot of admin view for editing an event"></a></td>
  <td><a href="https://github.com/user-attachments/assets/1d9e06c5-e869-462c-9112-6aba92e8b00c"><img src="https://github.com/user-attachments/assets/1d9e06c5-e869-462c-9112-6aba92e8b00c" alt="screenshot of admin view for emailing guests" title="screenshot of admin view for emailing guests"></a></td>
  <td><a href="https://github.com/user-attachments/assets/837d0683-af48-4273-839b-123ad07cd274"><img src="https://github.com/user-attachments/assets/837d0683-af48-4273-839b-123ad07cd274" alt="screenshot of a sample event page, including RSVP form" title="screenshot of a sample event page, including RSVP form"></a></td>
</tr></table>

Your invitees will receive emails containing personalized links back to your Seevooplay instance. They won't have to create any sort of account (or log in) to RSVP to your event; a UUID in their link tells Seevooplay who they are. *This means that forwarded links are problematic: If Alice forwards her invitation to Bob, Bob can RSVP as Alice.* In other words, from a security standpoint, Seevooplay is about as naive as it gets. For the casual, personal use cases Seevooplay is designed for, however, this model works. If it spooks you, your parties are much higher stakes than mine, and you should look for a different solution. :)

Seevooplay is free software, licensed under the terms of the GNU General Public License, Version 3. See the included COPYING file for details.

For slightly more context, [read the original release announcement](https://www.mahnamahna.net/blog/i-made-this-introducing-seevooplay/).

---

# Installation

Seevooplay can be run as a standalone project, or integrated with an existing Django project.

## Run as a standalone project

There is not (yet) a containerized distribution of Seevooplay, so there is a small bit of setup work to do if you'd like to selfhost a standalone instance. As of version 2.0, Seevooplay is a uv project. If you don't have uv, [grab a copy](https://docs.astral.sh/uv/getting-started/installation/) before proceeding.

1. Download the Seevooplay distribution and extract to a folder, or `git clone` it.
2. Copy config/settings/local.py.example to config/settings/local.py and edit local.py to match your server's particulars.
3. `cd` into Seevooplay's directory and use `uv` to fetch Seevooplay's dependencies and set up its virtual environment:
```bash
uv sync
uv run ./manage.py migrate
uv run ./manage.py collectstatic
```
4. Now do `uv run ./manage.py sendtestemail` to ensure your setup can send mail.
5. Now `uv run ./manage.py createsuperuser` will walk you through creating a superuser.
6. Fire up the Django development server with `uv run ./manage.py runserver` if you are test-driving Seevooplay. In production, you'll want to put your webserver of choice in front of the project. ([Do not](https://docs.djangoproject.com/en/5.2/ref/django-admin/#runserver) run the development server in production!)
7. In your browser, navigate to http://yourdomain/admin and log in with your superuser credentials to poke around and create your first event in Seevooplay. As long as you remain logged in, you can view your first event at http://yourdomain/rsvp/1.

## Integrate with an existing Django project

1. Add Seevooplay to your project with `uv add seevooplay`.
2. Add to INSTALLED_APPS in your settings.py:
```python
'djrichtextfield',  # required for seevooplay
'seevooplay',
```
3. Add settings for django-richtextfield in your settings.py. See [django-richtextfield's docs](https://github.com/jaap3/django-richtextfield#django-rich-text-field) for details, or copy the DJRICHTEXTFIELD_CONFIG stanza from Seevooplay's config/settings/base.py.
4. In your main urls.py, include Seevooplay's URLs (make sure `include` is imported from `django.urls`):
```python
path('seevooplay/', include('seevooplay.urls')),
```
This mounts Seevooplay's routes under `/seevooplay/`, giving you paths like `/seevooplay/rsvp/<event_id>/`.

5. From within your project's virtual environment:
```bash
uv run ./manage.py migrate
uv run ./manage.py collectstatic
```
6. There should now be a Seevooplay section in your project's admin, where you can start kicking the tires.

---

# What Seevooplay Lacks

- The ability to message invitees using anything other than email. Seevooplay cannot send text messages to phone numbers, for instance, for the simple reason that there is no cost-free or even hassle-free way for a self-hosted application to do that, due to carrier restrictions targeting spam and abuse.
- Internationalization. I welcome pull requests to change this.
- HTML emails. Plain text emails don't bother me much, but perhaps I'll do these someday.
- Comprehensive documentation. If anyone other than me ends up using this, the docs will get better. In the meantime, if you try using Seevooplay and run into trouble, please open an issue on GitHub. I will help if I can.
- Perfection. This software was crafted to scratch a personal itch. It almost certainly has bugs. If you discover one, or you have a suggestion for improving the code, please open an issue on GitHub.
- ~~'Add to calendar' functionality. This is probably something I'll hack on at some point.~~ **(Done in 2.0!)**
- ~~Tests. Another thing I'm likely to throw together at some point.~~ **(Done in 2.0!)**
