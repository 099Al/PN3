from configs import config
from db.queriesDB import upd_balance,add_to_orders, log_orders,log_balance,log_orders

MODE = config.MODE
ALGO_NAME = 'A1'


def f_alg1(unix_curr_time):
    api = None
    calc_res = None

    if MODE == "TRADE":
        from api.cexioNewApi import Api

        calc_res = CALCULTAION

        api = Api(config.API_USER, config.API_KEY, config.API_SECRET)
        #set or cancel
        #save into db


    if MODE == 'TEST':
        from emulatorApi.cexioEmNewApi import emulatorApi

        api = emulatorApi('TEST_USER',unix_curr_time)



    # if res == buy:
    #     api.buy_lmit_otder
    # if res == sell:
    #     api.sell_limit order
    # if res == ...

    # api.sell_limit_order(amount=0.000003,price=3000)
    # api.buy_limit_order(amount=0.000003, price=3000)

    res = api.buy_limit_order(amount=0.00042277, price=3000)

    data = res['data']
    status = data['status']

    from db.connection import DBConnect
    conn = DBConnect().getConnect()

    if status != 'REJECTED':
        upd_balance(data,conn)
        add_to_orders(data,ALGO_NAME,conn)

    log_orders(data,ALGO_NAME,conn)

    conn.comit()
    conn.close()



    #api.buy_limit_order(amount=0.00042277, price=3000)
    #save buy order to DB  db/queriesDB.py



    #values = calculations

    #res = set (price,amount,side)

    #save res into db (transactons, curr_state)


if __name__ == '__main__':
    f_alg1(1690089409000)
