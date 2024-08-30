from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from django.core.exceptions import PermissionDenied
from .settings import BASE_DIR

from datetime import datetime
import os
import gzip
from itertools import islice

def is_authenticated_user(request):
    """
    Function to see if user is authenticated.
    """
    return request.user.is_authenticated

def get_datetime_from_line(line):
    """
    Function to get date and time from a line.
    """
    try:
        date, time = line.split(" ")[0], line.split(" ")[1].split(".")[0]
        return datetime.strptime("%s %s" % (date, time), "%Y-%m-%d %H:%M:%S")
    except:
        return None

def get_log_status(line):
    """
    Function to get the status of a log.
    """
    try:
        return (line.split("|")[1].strip())
    except:
        return ""


def is_file_relevant(filename, start_date, end_date):
    """
    Function to read date creation of gzip files.
    """
    try:
        file_date_str = filename.split(".")[1].split("_")[0]
        file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
        return file_date >= start_date and file_date <= end_date
    except:
        return False

def read_lines_from_file(filepath, start_date, end_date, ignore_info=False, ignore_table=False):
    """
    Function to read lines based on specific file type requirementts.
    """
    is_gzip = filepath.endswith(".gz")
    open_func = gzip.open if is_gzip else open
    mode = 'rt' if is_gzip else 'r'
    found_time = False
    lines = []
    with open_func(filepath, mode) as f:
        for line in f:
            line = line.strip()
            line_datetime = get_datetime_from_line(line)
            line_log_type = get_log_status(line)
            line_is_table = line.startswith('|') or line.startswith('+')

            if not line or len(lines) >= 1000 or (ignore_info and line_log_type == "INFO") or (ignore_table and line_is_table):
                continue
            
            if line_datetime:
                if start_date <= line_datetime <= end_date:
                    found_time = True
                    lines.append(line)
            else:
                lines.append(line)
    if not found_time:
        return []
    return lines
    
def file_list (file_paths, searched_files = []):
    """
    Function that takes in a list of pathnames and returns a dictionary of the files within the directories
    @param file_paths: list of pathnames we want to search
    @param searched_files: list of specific filenames to search for
    @return: dictionary of files within the directories along with their timestamps
    """
    file_dict = {}
    for path in file_paths:
        file_dict[str(path)] = []
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)) and (file in searched_files or not searched_files):
                timestamp = os.path.getmtime(os.path.join(path, file))
                timestamp = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                file_dict[str(path)].append([file,timestamp])
        file_dict[str(path)] = sorted(file_dict[str(path)], key=lambda x:x[1], reverse=True)
            
    return file_dict

def file_list_individual (file_paths, searched_files = [], numfiles = 10):
    """
    Function that takes in a list of pathnames and returns a list of the files within the directories
    @param file_paths: list of pathnames we want to search
    @param searched_files: list of specific filenames to search for
    @return: dictionary of files within the directories along with their timestamps
    """
    file_list = []
    for path in file_paths:
        for dir_path, dir_names, files in os.walk(path):
            for file in files:
                if file in searched_files or not searched_files:
                    timestamp = os.path.getmtime(os.path.join(dir_path, file))
                    timestamp = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    file_list.append([file,timestamp])
            
        file_list = sorted(file_list, key=lambda x:x[1], reverse=True)
            
    if not file_list:
        file_list = [['No file found', '']]
    return file_list[:numfiles]