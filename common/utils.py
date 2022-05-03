import os
import random
import string
import time
from datetime import datetime

from django.conf import settings
from django.template.defaultfilters import slugify


def get_upload_file_path(path, upload_name):
    # Generate date based path to put uploaded file.
    date_path = datetime.now().strftime('%Y/%m/%d')

    # Complete upload path (upload_path + date_path).
    upload_path = os.path.join(settings.UPLOAD_URL, path, date_path)
    full_path = os.path.join(settings.BASE_DIR, upload_path)
    make_sure_path_exist(full_path)
    file_name = slugify_filename(upload_name)
    return os.path.join(full_path, file_name).replace('\\', '/'), os.path.join('/', upload_path, file_name).replace('\\', '/')


def slugify_filename(filename):
    """ Slugify filename """
    name, ext = os.path.splitext(filename)
    slugified = get_slugified_name(name)
    return slugified + ext


def get_slugified_name(filename):
    slugified = slugify(filename)
    return slugified or get_random_string()


def get_random_string():
    return ''.join(random.sample(string.ascii_lowercase * 6, 6))


def make_sure_path_exist(path):
    if os.path.exists(path):
        return
    os.makedirs(path, exist_ok=True)


def format_time(dt: datetime, fmt: str = ''):
    fmt_str = fmt or '%Y-%m-%d %H:%M:%S'
    return dt.strftime(fmt_str)


def get_year(dt: datetime) -> int:
    return dt.year


def get_now() -> str:
    return format_time(datetime.now())


def format_time_from_str(date_time_str: str, fmt: str = ''):
    fmt_str = fmt or '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(date_time_str, fmt_str)


def transform_time_to_str(t: int):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))