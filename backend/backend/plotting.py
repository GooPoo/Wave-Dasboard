from datetime import datetime, timedelta
from os.path import join, exists
import xarray as xr
import pandas as pd
import numpy as np
from itertools import islice
from django.http import JsonResponse

def parse_datetime(date):
    if not date:
        return None 

    if len(date) != 10:
        return None
    
    year = int(date[0:4])
    if year not in range(1990, 2100):
        return None

    month = int(date[4:6])
    if month not in range(1, 13):
        return None

    day = int(date[6:8])
    if day not in range(1, 32):
        return None

    hour = int(date[8:10])
    if hour not in range(0, 24):
        return None
    
    return datetime(year=year, month=month, day=day, hour=hour)

def get_most_recent_12_hour_period(dt):
    if dt.hour < 12:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        return dt.replace(hour=12, minute=0, second=0, microsecond=0)

def extract_data(data, start_date, end_date):
    """Helper function to extract data from datasets."""
    hour = [pd.to_datetime(str(value)).strftime("%Y%m%d%H") for value in data["time"].sel(time=slice(start_date, end_date)).values[:12]]
    hs_values = [str(value[0]) if not np.isnan(value[0]) else None for value in data["hs"].sel(time=slice(start_date, end_date)).values[:12]]
    tp_values = [str(value[0]) if not np.isnan(value[0]) else None for value in data["tp"].sel(time=slice(start_date, end_date)).values[:12]]
    dp_values = [str(value[0]) if not np.isnan(value[0]) else None for value in data["dp"].sel(time=slice(start_date, end_date)).values[:12]]
    
    return hour, hs_values, tp_values, dp_values

def process_request_12hours(request, path_format, filename_format):
    """Helper function to handle 12 hours data extraction requests."""
    start_date = parse_datetime(request.GET.get('start-date', None))
    end_date = parse_datetime(request.GET.get('end-date', None))

    if not start_date or not end_date:
        return JsonResponse({"error": "Invalid date."}, status=405)

    response = {
        "hour": [],
        "hs_values": [],
        "tp_values": [],
        "dp_values": [],
    }

    date_ = get_most_recent_12_hour_period(start_date)
    while date_ < end_date:
        file_path = join(path_format.format(date_), filename_format.format(date_))
        if exists(file_path):
            with xr.load_dataset(file_path) as data:
                hour, hs_values, tp_values, dp_values = extract_data(data, start_date, end_date)
                response["hour"].extend(hour)
                response["hs_values"].extend(hs_values)
                response["tp_values"].extend(tp_values)
                response["dp_values"].extend(dp_values)
        date_ += timedelta(hours=12)

    return JsonResponse(response)