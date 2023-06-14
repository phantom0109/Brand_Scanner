import datetime as dt

import pytz


def current_india_time():
    return dt.datetime.now(pytz.timezone("Asia/Kolkata"))
