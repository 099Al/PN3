from datetime import datetime
import configparser

from _data.data import get_new_data

from configs import config
import algorithms as algo

MODE = config.MODE
#MODE = 'TRAID'

#---Вынести в config ???
t_start = '2023-07-22 15:00:00'
time_step = 120
#init_balance
init_btc = 0.0015
init_usd = 100
#-----------------

valid_pairs = ['BTC/USD']





if __name__ == '__main__':

    #INIT BALANCE
    from db.connection import DBConnect
    conn = DBConnect().getConnect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM BALANCE')
    cursor.execute('INSERT INTO BALANCE (CURR,AMOUNT) VALUES(?,?)',('BTC',init_btc))
    cursor.execute('INSERT INTO BALANCE (CURR,AMOUNT) VALUES(?,?)',('USD',init_usd))
    conn.commit()
    conn.close()

    exit()



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

        #---Вычесления------------
        #.....
        # set_flag -> return id _order
        algo.a1.manager.f_alg1(curr_unix_time)


        buy_req = api.buy_limit_order(0.00042277, 30100.0, 1)
        # save _order in db

        #---вычисления------------
        #check flags(MODE)



        #В PROD делаем запрос(по id) и возвращаем результат?
        #В TEST делаем запрос к im_table на промежутке от времени установки флага до данного запроса






        #algorithms (set flags/ remove flags)



        if n>5:
            break
