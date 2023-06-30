import datetime
from datetime import datetime
import tzlocal
import time

'''convert string to datetime'''
def try_strptime(s, fmts=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']):
    for fmt in fmts:
        try:
            return datetime.datetime.strptime(s, fmt)
        except:
            pass

    return None

def unix_to_date(unixtime):
    unix_timestamp = float(unixtime)
    date_time = datetime.fromtimestamp(unix_timestamp)
    return date_time.strftime('%Y-%m-%d %H:%M:%S')

def unix_to_localdate(unixtime):
    unix_timestamp = float(unixtime)
    local_timezone = tzlocal.get_localzone()  # get pytz timezone
    local_time = datetime.fromtimestamp(unix_timestamp, local_timezone)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')


def unix_time_sec():
    return int(time.time())

if __name__ == '__main__':
    res = unix_to_localdate(1547576061)
    res2 = unix_to_date(1547586630)
    print('local :',res)
    print(res2)

    import ccxt

    import hmac
    import hashlib

    message = 'a' + 'b' + 'c'
    signature = hmac.new(bytearray('ff'.encode('utf-8')), message.encode('utf-8'),
                         digestmod=hashlib.sha256).hexdigest().upper()
    print(signature)

