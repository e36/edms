import calendar
import time


def convert_timestamp(timestamp, pattern="%Y-%m-%dT%H:%M:%S", strip=19):
    # converts the reddit modmail conversation timestamp to unix epoch
    # strip can be used to increase or decrease how much of the timestamp is truncated before running through strptime
    # 2018-04-21T14:25:11

    # convert to epoch time
    epoch = calendar.timegm(time.strptime(timestamp[:strip], pattern))

    return epoch


def get_now_utc_epoch():
    """
    Returns the epoch
    :return:
    """
    return int(time.time())
