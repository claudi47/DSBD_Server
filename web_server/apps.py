import sys

from django.apps import AppConfig

from web_server.transaction_scheduler import init_scheduler


class WebServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_server'
