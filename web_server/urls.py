from django.contrib import admin
from django.urls import path, include
from web_server.views import *

urlpatterns = [
    path('goldbet/', bet_data_view),
    path('bwin/', bet_data_view),
    path('csv/', url_csv_view),
    path('stats', stats_view),
    path('settings', settings_view),
    path('validation/', validation_view),
]