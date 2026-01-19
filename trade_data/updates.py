from _configs import config

from trade_data.queriesDB import save_history_tik,log_orders,balance_state

valid_pairs = ['BTC/USD']

def get_new_data(mode,pair,curr_time=None,conn=None):


    if pair not in valid_pairs:
        print('Not valid pair')
        exit()

    p1,p2 = pair.split('/')


    if mode == 'TEST':
        from src.api.emulatorcexio.emulator_api import EmulatorApi
        #Делается запрос к источнику(либо к сайту, либо к эмулятору)
        api = EmulatorApi(curr_time)
        #emApi.currentTime=curr_time  #В случае эмуляции ставим время, в которое делается запрос
    if mode == 'TRAID':
        from src.api.cexio.cexioNewApi import Api
        api = Api(config.API_USER, config.API_KEY, config.API_SECRET)


    res = api.trade_history(f'{p1}-{p2}')
    tiks = res['data']['trades']

    # save _data into trade_data  #or save into Memory ?
    save_history_tik(tiks,conn)

    print('curr',res)

    return None

def check_orders(curr_time,conn=None):
    flag_con = 0  # 1- коннект не передавался, а создался внутри функции
    if conn is None:
        flag_con = 1
        from trade_data.db.connection import DBConnect
        conn = DBConnect().getConnect()


    cursor = conn.cursor()

    res = cursor.execute('SELECT id,unix_date,algo FROM ACTIVE_ORDERS')
    l_active_orders = res.fetchall()

    if mode == 'TEST':
        from src.api.emulatorcexio.emulator_api import EmulatorApi
        #Делается запрос к источнику(либо к сайту, либо к эмулятору)
        api = EmulatorApi(config.USER_NAME, curr_time)
        #emApi.currentTime=curr_time  #В случае эмуляции ставим время, в которое делается запрос
    if mode == 'TRAID':
        from src.api.cexio.cexioNewApi import Api
        api = Api(config.API_USER, config.API_KEY, config.API_SECRET)


    l_remined_orders = api.open_orders()['data']
    l_remined_id = [x['orderId'] for x in l_remined_orders]

    l_done_orders = [x for x in l_active_orders if x[0] not in l_remined_id]

    for order in l_done_orders:
        data = {'OrderId': order[0], 'serverCreateTimestamp': order[1], 'status': 'DONE'}
        algo = order[2]

        balance_state(data,True,algo,conn) #изменения баланса на стороне программы
        log_orders(data,None, ALGO_NAME, conn)

    if flag_con == 1:
        conn.close()
