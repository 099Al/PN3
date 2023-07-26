from datetime import datetime
import configparser

from data.data import get_new_data

from configs import config


MODE = 'TEST'
#MODE = 'TRAID'

t_start = '2023-07-22 15:00:00'
time_step = 120


valid_pairs = ['BTC/USD']


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

        curr_unix_time = 1690089409.298
        get_new_data(MODE,'BTC/USD',curr_unix_time)

        #Делаем вычесления

        #check flags(MODE)

        #В PROD делаем запрос(по id) и возвращаем результат?
        #В TEST делаем запрос к im_table на промежутке от времени установки флага до данного запроса


        # set_flag -> return id order
        # save order in db



        #algorithms (set flags/ remove flags)



        if n>5:
            break
