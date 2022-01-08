import datetime

import requests
from django.http import HttpResponse
from pytz import utc
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.models import User, Settings

# In Django, a view determines the content of a web page
# views.py is where we handle the request/response logic of our web server

@api_view(['GET'])
def stats_view(request):
    match request.query_params['stat']:
        case "1":
            stat_from_module = requests.get("http://stats_settings:8500/stats?stat=1")
            if not stat_from_module.ok:
                return Response('Bad Response', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return HttpResponse(stat_from_module.text, content_type="application/json")
        case "2":
            stat_from_module = requests.get("http://stats_settings:8500/stats?stat=2")
            if not stat_from_module.ok:
                return Response('Bad Response', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return HttpResponse(stat_from_module.text, content_type="text/plain")
        case "3":
            stat_from_module = requests.get("http://stats_settings:8500/stats?stat=3")
            if not stat_from_module.ok:
                return Response('Bad Response', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return HttpResponse(stat_from_module.text, content_type="application/json")
        case "4":
            stat_from_module = requests.get("http://stats_settings:8500/stats?stat=4")
            if not stat_from_module.ok:
                return Response('Bad Response', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return HttpResponse(stat_from_module.text, content_type="application/json")
    return Response("wow", status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def settings_view(request):
    try:
        match request.query_params['setting']:
            case 'ban':
                response = requests.post('http://stats_settings:8500/ban', json=request.data)
                if not response.ok:
                    return Response('Bad Response', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response('Ok', status=status.HTTP_200_OK)
            case 'max_r':
                response = requests.post('http://stats_settings:8500/researches', json=request.data)
                if not response.ok:
                    return Response('Bad Response', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response('Ok', status=status.HTTP_200_OK)
            case 'toggle':
                response = requests.post('http://stats_settings:8500/toggle', json=request.data)
                if not response.ok:
                    return Response('Bad Response', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response('Ok', status=status.HTTP_200_OK)
    except KeyError:
        return Response('BaD qUeRy PaRaMs', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def validation_view(request):
    user_id = request.query_params['user_id']
    website = request.query_params['website']
    try:
        user_model = User.objects.get(pk=user_id)
    except:
        return Response('User does not exist')

    banned = user_model.ban_period
    if banned is not None:
        banned = banned.replace(tzinfo=utc)
        if banned >= datetime.datetime.now().replace(tzinfo=utc):
            return Response('banned')

    researches_threshold = user_model.max_research
    researches_count = user_model.searches.count()

    if researches_count >= researches_threshold != -1:
        return Response('reached_max')

    if website == 'goldbet':
        is_enabled = Settings.objects.get(pk=1).goldbet_research
        if not is_enabled:
            return Response("disabled")
    elif website == 'bwin':
        is_enabled = Settings.objects.get(pk=1).bwin_research
        if not is_enabled:
            return Response("disabled")

    return Response('bravo')
