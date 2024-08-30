from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Import User model
from django.shortcuts import redirect, render, resolve_url
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView, View
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from two_factor.views import OTPRequiredMixin
from two_factor.views.utils import class_view_decorator
from django.core.exceptions import PermissionDenied

from datetime import datetime, timedelta
from os.path import join, exists
import xarray as xr
import pandas as pd
import numpy as np
import os
from itertools import islice
from .logging import *
from .plotting import *
from .settings import PROJECT_PATH, BASE_DIR, PREDICTIONS_PATH, FORECASTS_PATH, BUOY_PATH, WIND_PATH, LOG_PATH, CSV_PATH

class HomeView(TemplateView):
    template_name = 'home.html'


class RegistrationView(FormView):
    template_name = 'registration.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        # Check if any users exist in the auth_user table
        if User.objects.exists():
            return redirect('registration_disabled_page')  # Redirect to a page indicating registration is disabled
        else:
            form.save()  # Your regular registration logic here
            return redirect('registration_complete')


class RegistrationCompleteView(TemplateView):
    template_name = 'registration_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        return context

@class_view_decorator(never_cache)
class CombinedView(OTPRequiredMixin, TemplateView):
    template_name = 'combined.html'

@class_view_decorator(never_cache)
class PredictionView(OTPRequiredMixin, TemplateView):
    template_name = 'prediction.html'

@class_view_decorator(never_cache)
class ForecastView(OTPRequiredMixin, TemplateView):
    template_name = 'forecast.html'

@class_view_decorator(never_cache)
class BuoyView(OTPRequiredMixin, TemplateView):
    template_name = 'buoy.html'

@class_view_decorator(never_cache)
class WindView(OTPRequiredMixin, TemplateView):
    template_name = 'wind.html'

class LoggingView(OTPRequiredMixin, TemplateView):
    template_name = 'logging.html'

    def get(self, request):
        if os.path.exists(LOG_PATH):
            directory = LOG_PATH
        else:
            directory = os.path.join(BASE_DIR, "logs")
        log_files = [file for file in os.listdir(
            directory) if os.path.isdir(join(directory, file))]
        return render(request, "logging.html", {
            "log_files": log_files
        })

# Logs, if you want to see the full code, check backend/backend/logging.py
def log_request(request):
    """
    Handles GET requests to return logs.
    """
    if not is_authenticated_user(request):
        raise PermissionDenied
    if request.method != "GET":
        return JsonResponse({})

    start_date = datetime.strptime(request.GET.get("startDate"), "%Y-%m-%d %H:%M")
    end_date = datetime.strptime(request.GET.get("endDate"), "%Y-%m-%d %H:%M")
    ignore_info = request.GET.get("ignoreINFO", "false") == "true"
    ignore_table = request.GET.get("ignoreTable", "false") == "true"

    if os.path.exists(os.path.join(LOG_PATH, request.GET.get("file", ""))):
        directory = os.path.join(LOG_PATH, request.GET.get("file", ""))
    else:
        directory = os.path.join(BASE_DIR, "logs", request.GET.get("file", ""))
    
    gzFiles = [file for file in os.listdir(
        directory) if os.path.isfile(os.path.join(directory, file)) and file.endswith(".gz") and is_file_relevant(file, start_date, end_date)]
    logFiles = [file for file in os.listdir(
        directory) if os.path.isfile(os.path.join(directory, file)) and file.endswith(".log")]

    result = {}
    for file in gzFiles + logFiles:
        lines = read_lines_from_file(os.path.join(directory, file), start_date, end_date, ignore_info, ignore_table)
        if lines:
            result[file] = lines

    return JsonResponse(result)

def file_arrival_times(request):
    """
    Handles GET requests to return file arrival times.
    """
    if request.user.is_authenticated == False:
        raise PermissionDenied
    
    if request.method == "GET":
        response = {}
        log_paths = [LOG_PATH]
        log_files = []

        buoy_paths = [BUOY_PATH]
        buoy_files = []

        prediction_paths = [PREDICTIONS_PATH]
        prediction_files = []

        forecast_paths = [FORECASTS_PATH]
        forecast_files = []

        wind_paths = [WIND_PATH]
        wind_files = []

        csv_paths = [CSV_PATH]
        csv_files = []

        response = {}
        try:
            response['Log'] = file_list_individual(log_paths, log_files)
            response['Buoy'] = file_list_individual(buoy_paths, buoy_files)
            response['Prediction'] = file_list_individual(prediction_paths, prediction_files)
            response['Forecast'] = file_list_individual(forecast_paths, forecast_files)
            response['Wind'] = file_list_individual(wind_paths, wind_files)
            response['CSV'] = file_list_individual(csv_paths, csv_files)
        except:
            response['Error'] = [['Error', 'File not found']]

        return JsonResponse(response)

#Plots, if you want to see the full code, check backend/backend/plotting.py
def prediction_12hours(request):
    """Handles GET requests to return prediction data."""
    if request.user.is_authenticated == False:
        return PermissionDenied

    if request.method == "GET":
        path_format = join(PREDICTIONS_PATH, "{0:%Y%m}")
        filename_format = "IDY40102.ML.False.afs_point_{0:%Y%m%d%H}.nc"
        return process_request_12hours(request, path_format, filename_format)
    return JsonResponse({"error": "This endpoint only supports GET requests."}, status=405)

def forecast_12hours(request):
    """Handles GET requests to return forecast data."""
    if request.user.is_authenticated == False:
        return PermissionDenied

    if request.method == "GET":
        path_format = join(FORECASTS_PATH, "{0:%Y-%m}")
        filename_format = "IDY40102.afs_point_{0:%Y%m%d%H}.nc"
        return process_request_12hours(request, path_format, filename_format)
    return JsonResponse({"error": "This endpoint only supports GET requests."}, status=405)

def buoy_12hours(request):
    """
    Handles GET requests to return buoy data.
    """
    if request.user.is_authenticated == False:
        return PermissionDenied

    if request.method == "GET":
        start_date = parse_datetime(request.GET.get('start-date', None))
        end_date = parse_datetime(request.GET.get('end-date', None))
        xarray_cache = {}

        # Validate the date
        if start_date and end_date:
            response = {
                "hour": [],
                "hs_values": [],
                "tp_values": [],
                "dp_values": [],
            }

            date_ = start_date
            while date_ <= end_date:
                # Get the monthly prediction file
                month_file = join(
                    BUOY_PATH,
                    f"{date_.year}",
                    f"{date_.year}-{date_.month:02d}-buoy-inner-94x72-ftp.nc",
                )

                if not exists(month_file):
                    print("doesnt exist ", month_file)
                else:
                    if month_file not in xarray_cache:
                        with xr.load_dataset(month_file) as data:
                            xarray_cache[month_file] = data

                    buoy_data = xarray_cache[month_file]

                    response["hour"].append(pd.to_datetime(str(date_)).strftime("%Y%m%d%H"))
                    hs = buoy_data["Hs"].sel(time=date_).values.item()
                    response["hs_values"].append(hs if not np.isnan(hs) else None)
                    tp = buoy_data["Tp"].sel(time=date_).values.item()
                    response["tp_values"].append(tp if not np.isnan(tp) else None)
                    dp = buoy_data["Dp"].sel(time=date_).values.item()
                    response["dp_values"].append(dp if not np.isnan(dp) else None)

                date_ += timedelta(hours=1)

            return JsonResponse(response)
        else: 
            return JsonResponse({"error": "Invalid date."}, status=405)
    else:
        return JsonResponse({"error": "This endpoint only supports GET requests."}, status=405)

def wind_12hours(request):
    """
    Handles GET requests to return wind data.
    """
    if request.user.is_authenticated == False:
        return PermissionDenied

    if request.method == "GET":
        start_date = parse_datetime(request.GET.get('start-date', None))
        end_date = parse_datetime(request.GET.get('end-date', None))
        station = int(request.GET.get('station', None))
        xarray_cache = {}

        # Validate the date
        if start_date and end_date:
            response = {
                "hour": [],
                "ws_values": [],
                "dp_values": [],
            }

            date_ = start_date
            while date_ <= end_date:
                # Get the monthly prediction file
                month_file = join(
                    WIND_PATH,
                    f"{date_.year}",
                    f"{date_.year}-{date_.month:02d}-wind.nc",
                )

                if not exists(month_file):
                    print("doesnt exist ", month_file)
                else:
                    if month_file not in xarray_cache:
                        xarray_cache[month_file] = xr.load_dataset(month_file)

                    buoy_data = xarray_cache[month_file]

                    print(type(date_), date_)
                    response["hour"].append(pd.to_datetime(str(date_)).strftime("%Y%m%d%H"))
                    ws = buoy_data["wind_speed"].sel(time=date_).values[station].item()
                    response["ws_values"].append(ws if not np.isnan(ws) else None)
                    dp = buoy_data["wind_direction"].sel(time=date_).values[station].item()
                    response["dp_values"].append(dp if not np.isnan(dp) else None)

                date_ += timedelta(hours=1)

            return JsonResponse(response)
        else: 
            return JsonResponse({"error": "Invalid date."}, status=405)
    else:
        return JsonResponse({"error": "This endpoint only supports GET requests."}, status=405)

#Other
def registration_disabled_page(request):
    return render(request, 'registration_disabled.html')

