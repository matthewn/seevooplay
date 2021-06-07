from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    enable_nav_sidebar = False
    site_header = 'Seevooplay'
    site_title = 'Seevooplay'

    def get_app_list(self, request):
        """
        Override this AdminSite method to reorder the app list on the index
        page. Must return a list of dicts.
        """
        app_list = super(CustomAdminSite, self).get_app_list(request)
        if not app_list:  # covers case where user has no permissions
            return
        neworder = [
            'seevooplay',
            'auth',
        ]
        return [d for lbl in neworder for d in app_list if d["app_label"] == lbl]
