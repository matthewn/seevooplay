from django.contrib.admin.apps import AdminConfig


class CustomAdminConfig(AdminConfig):
    """ Enable our custom admin. """
    default_site = 'config.admin.CustomAdminSite'
