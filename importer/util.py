from django.utils import timezone
from datetime import datetime, timedelta

import pytz
import hashlib

def compute_file_hash(file):
    """Reads the file, computes the SHA-256 hash
    """
    # Read the content and encode it to bytes
    file.seek(0)
    content = file.read().encode('utf-8')
    file.seek(0)
    # Compute the SHA-256 hash
    return hashlib.sha256(content).hexdigest()

def convert_to_utc_datetime(date_str):
    """Convert a date string to a timezone-aware datetime"""
    # Define the format of the date string
    date_format = "%Y-%m-%d %H:%M:%S"
    # Parse the string into a naive datetime object
    naive_datetime = datetime.strptime(date_str, date_format)
    # Assign the UTC timezone
    utc_timezone = pytz.utc
    # Convert the naive datetime to a timezone-aware one
    return utc_timezone.localize(naive_datetime)


def to_localtime(utc,timezone):
    """Convert datetime utc to local time
    
    Output format (both strings)
    time: Sat Jan 27 13:23 2024
    utc_delta: +2

    with time rounded to the nearest minute
    """
    local_zone = pytz.timezone(timezone)
    local_time = utc.astimezone(local_zone)
    utc_delta = int(local_time.utcoffset().total_seconds()/3600)
    # Round to the nearest minute
    local_time = local_time + timedelta(seconds=30)
    local_time = local_time.replace(second=0, microsecond=0)
    # like ctime() without the seconds
    rounded_str = local_time.strftime("%a %b %d %H:%M %Y")
    return {'time': rounded_str,
            'utc_delta': f"{utc_delta:+d}"}