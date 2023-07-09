from datetime import datetime
from data.data import get_new_data

import configparser

MODE = 'TEST'
t_start = '2023-07-05 12:30:01'
time_step = 120


if __name__ == '__main__':

    conf_data = configparser.ConfigParser()
    conf_data.read('../configs/config.ini')
    period = int(conf_data['RUN']['REQUEST_PERIOD'])

    dt_start = datetime.strptime(t_start, '%Y-%m-%d %H:%M:%S')
    dt_unix_start = int(dt_start.timestamp())





    n=0
    curr_unix_time=dt_unix_start

    while True:
        n=n+1
        curr_unix_time=curr_unix_time+period


        get_new_data(MODE,'',curr_unix_time)

        #check flags


        #algorithms


        if n>100:
            break
