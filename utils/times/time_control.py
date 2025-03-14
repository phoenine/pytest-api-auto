import time
from datetime import datetime


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"Function '{func.__name__}' took {elapsed_time:.2f} milliseconds")
        return result

    return wrapper


def timestamp_to_datetime(timestamp: int) -> str:
    """
    Convert timestamps to date format
    :param timestamp: timestamp
    :return: date
    """
    if isinstance(timestamp, int):
        timeStamp = float(timestamp / 1000)
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime
    else:
        raise "Please pass in the correct timestamp."


def datetime_to_timestamp(timeStr: str) -> int:
    """
    Convert date format to timestamp
    :param timeStr: date
    :return: timestamp
    """
    try:
        datetimeFormat = datetime.strptime(str(timeStr), "%Y-%m-%d %H:%M:%S")
        timestamp = int(
            time.mktime(datetimeFormat.timetuple()) * 1000.0
            + datetimeFormat.microsecond / 1000.0
        )
        return timestamp
    except ValueError:
        raise 'The date format is incorrect, and the format needs to be passed in as "%Y-%m-%d %H:%M:%S"'


def get_current_time():
    """
    Get the current time, date format: 2021-12-11 12:39:25
    :return: date
    """
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return localtime

