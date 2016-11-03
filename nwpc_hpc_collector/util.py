from datetime import datetime, date, time, timedelta


def json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat(' ')  # obj.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, time):
        return obj.strftime('%H:%M:%S')
    elif isinstance(obj, timedelta):
        return {'day': obj.days, 'seconds': obj.seconds}
    else:
        raise TypeError('%r is not JSON serializable' % obj)