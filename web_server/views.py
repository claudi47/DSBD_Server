import datetime

import requests
from apscheduler.jobstores.base import JobLookupError
from django.http import HttpResponse
from pytz import utc
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from web_server.models import Search, BetData, User, Settings
from web_server.serializers import UserSerializer, SearchSerializer, BetDataSerializer, SettingsDataSerializer
from web_server.transaction_scheduler import transaction_scheduler, repeat_deco


@repeat_deco(3, reschedule_count=3, always_reschedule=True)
def rollback_function(search_id):
    # this is a query where we select the rows with that search_id and after we delete them
    BetData.objects.filter(search=search_id).delete()
    Search.objects.filter(pk=search_id).delete()  # delete of entry search with that primary key


# In Django, a view determines the content of a web page
# views.py is where we handle the request/response logic of our web server

@api_view(['POST'])  # returns a decorator that transforms the function in a APIView REST class
def bet_data_view(request):
    user_identifier = request.data.get('user_id')
    username = request.data.get('username')
    web_site = request.data.get('web_site')
    try:
        # Check if the user exists. If not, create a new one after the data validation!
        if not User.objects.filter(pk=user_identifier).exists():
            user = UserSerializer(data={'username': username, 'user_identifier': user_identifier})
            # 'raise_exception', if set True, raises a Validation Error exception in case of invalid data!
            if user.is_valid(raise_exception=True):  # verifies if the user is already created
                user.save()

        csv_url = ''
        search = SearchSerializer(data={'csv_url': csv_url, 'user': user_identifier, 'web_site': web_site})
        if search.is_valid(raise_exception=True):
            search_instance = search.save()
            # Adds the given job to the job list and wakes up the scheduler if it's already running.
            # Initiating relaxed compensating transaction (after 20 seconds)
            # misfire_grace_time is the time where the task can continue to run after the end of the deadline
            # If during a research the server shuts down and restarts, the replace_existing param allows to replace
            # the previous job whit the same ID
            transaction_scheduler.add_job(rollback_function, 'date',
                                          run_date=datetime.datetime.now() + datetime.timedelta(seconds=20),
                                          args=[search_instance.pk],
                                          id=str(search_instance.pk), misfire_grace_time=3600,
                                          replace_existing=True)
            # Pausing the job to make sure that the rollback function doesn't execute during the transaction,
            # which would invalid the transaction!
            transaction_scheduler.pause_job(str(search_instance.pk))
            bet_data_list = request.data['data']
            for element in bet_data_list:
                # **element passes the entire content of the dictionary where bet_data are present
                bet_data = BetDataSerializer(data={**element, 'search': search_instance.pk})
                if bet_data.is_valid(raise_exception=True):
                    bet_data.save()

            response_parsing_module = requests.post("http://stats_settings:8500/parsing", json=bet_data_list)
            if not response_parsing_module.ok:
                try:
                    # The 'reschedule_job' function will automatically resume the rollback job!
                    transaction_scheduler.reschedule_job(str(search_instance.pk), trigger='date')
                finally:
                    return Response('Error!', status=status.HTTP_400_BAD_REQUEST)
            else:
                associated_search_data = {'search_id': search_instance.pk, 'filename': response_parsing_module.text}
                transaction_scheduler.reschedule_job(job_id=str(search_instance.pk), trigger='date',
                                                     run_date=datetime.datetime.now() + datetime.timedelta(seconds=5))
                return Response(associated_search_data, status=status.HTTP_200_OK)

    except ValidationError:
        try:
            search_instance.pk
            transaction_scheduler.reschedule_job(job_id=str(search_instance.pk), trigger='date')
        except:
            pass
        raise
    except Exception as ex:
        try:
            search_instance.pk
            # Here we execute the rollback function (the decorator takes care of the retry logic)
            # Maybe, we could execute the job scheduler BEFORE the retry logic.
            rollback_function(search_instance.pk)
        except:
            pass

    return Response('Error!', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def url_csv_view(request):
    csv_url = request.data['url_csv']
    search_id = request.data['search_id']
    updated_search = SearchSerializer(Search.objects.get(pk=int(search_id)), data={'csv_url': csv_url}, partial=True)
    if updated_search.is_valid():
        try:
            # if in 5 seconds the job is removed, the rollback function is not called
            transaction_scheduler.remove_job(str(search_id))
        except JobLookupError:  # when the job is not found
            return Response('Job removal failed', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        updated_search.save()
        return Response('Csv transaction success', status=status.HTTP_201_CREATED)
    else:
        return Response('Csv transaction failed, data not valid', status=status.HTTP_400_BAD_REQUEST)


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
        return Response('First validation useless!')

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
