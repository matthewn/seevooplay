from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    enable_nav_sidebar = False
