from datetime import datetime, timedelta
from dateutil import tz

from dataStruct.constant import Constant


def cal_delta_timestamp(timestamp_a, timestamp_b):
    if timestamp_a > timestamp_b:
        tmp = timestamp_b
        timestamp_b = timestamp_a
        timestamp_a = tmp
    delta = timestamp_b - timestamp_a

    return delta/Constant.ONE_DAY_IN_MILLI/Constant.ONE_YEAR_IN_DAY

def timestamp_equal(timestamp_a, timestamp_b, granularity = 'd'):
    dt_a = timestamp_to_datetime(timestamp_a)
    dt_b = timestamp_to_datetime(timestamp_b)

    res = True
    if granularity in ('y', 'm', 'd', 'h'):
        res = res & (dt_a.year == dt_b.year)
        if granularity in ('m', 'd', 'h'):
            res = res & (dt_a.month == dt_b.month)
            if granularity in ('d', 'h'):
                res = res & (dt_a.day == dt_b.day)
                if granularity in ('h'):
                    res = res & (dt_a.hour == dt_b.hour)
    else:
        raise ValueError("Granularity Error.")

    return res



def timestamp_to_datetime(timestamp):
    # transfer timestamp to datetime (Beijing Time)
    return datetime.fromtimestamp(timestamp / 1000, tz=tz.gettz('Asia/Shanghai'))

def timestamp_to_symbolstr(timestamp):
    # formulate timestamp in symbol str, e.g. "25MAR2022"
    dt = timestamp_to_datetime(timestamp)
    symbol = dt.strftime("%d%b%y")
    return symbol.upper()

def date_to_timestamp(year, month, day, hour=0, minute=0, second=0):
    # specify Beijing time to timestamp
    return datetime_to_timestamp(datetime(year, month, day, hour, minute, second, tzinfo=tz.gettz("Asia/Shanghai")))

def datetime_to_timestamp(r_datetime):
    # transfer datetime to timestamp
    return int(datetime.timestamp( r_datetime ) * 1000)

def datetime_to_timestamp_tz0(r_datetime):
    # First set timezone as UTC0, Second transfer from datetime to timestamp
    return datetime_to_timestamp(r_datetime.replace(tzinfo=tz.gettz('UTC')))


def timestamp_floor(timestamp):
    # remove minute and seconds for timestamp
    old_dt = timestamp_to_datetime(timestamp)
    new_dt = old_dt.replace(minute=0, second=0)
    return datetime_to_timestamp(new_dt)
    # return int(np.floor(timestamp / Constant.ONE_HOUR_IN_MILLI) * Constant.ONE_HOUR_IN_MILLI)


def datetime_plus_deltaday(r_datetime, days=0, hours=0, minutes=0, seconds=0):
    return r_datetime + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

def timestamp_plus_deltaday(timestamp, days=0, hours=0, minutes=0, seconds=0):
    dt = datetime_plus_deltaday( timestamp_to_datetime(timestamp), days, hours, minutes, seconds )
    return datetime_to_timestamp( dt )





