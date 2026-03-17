from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import event_page, resend_page

urlpatterns = [
    path('rsvp/<int:event_id>/', event_page, name='invitation'),
    path('rsvp/<int:event_id>/<guest_uuid>/', event_page, name='event_page'),
    path('djrichtextfield/', include('djrichtextfield.urls')),
    path('', resend_page, name='resend_page'),
]

if settings.ROOT_URLCONF == 'seevooplay.urls':
    urlpatterns = [path('admin/', admin.site.urls)] + urlpatterns

if settings.DEBUG:  # pragma: no cover
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
