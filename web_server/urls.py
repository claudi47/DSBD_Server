from django.urls import path

from web_server.views import *

urlpatterns = [
    # path('goldbet/', bet_data_view),
    path('betdata/', bet_data_view),
    # path('csv/', url_csv_view),
    path('stats', stats_view),
    path('settings', settings_view),
    path('validation/', validation_view),
]