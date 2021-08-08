from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import email_guests, event_page

urlpatterns = [
    path('admin/email_guests/<int:event_id>/', email_guests, name='email_guests'),
    path('admin/', admin.site.urls),
    path('rsvp/<int:event_id>/', event_page, name='invitation'),
    path('rsvp/<int:event_id>/<guest_uuid>/', event_page),
    path('djrichtextfield/', include('djrichtextfield.urls'))
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
