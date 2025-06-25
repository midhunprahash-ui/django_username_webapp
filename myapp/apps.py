from django.apps import AppConfig


class MyappConfig(AppConfig): # Renamed class
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp' # Renamed app name
