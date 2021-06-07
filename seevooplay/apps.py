from django.contrib.admin.apps import AppConfig


class SeevooplayConfig(AppConfig):
    name = 'seevooplay'

    def ready(self):
        import seevooplay.signals  # noqa F401
