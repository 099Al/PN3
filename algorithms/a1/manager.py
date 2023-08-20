from configs import config
from db.queriesDB import upd_balance,upd_active_orders, log_orders,log_balance,log_orders

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
    #     api.sell_limit _order
    # if res == ...

    # api.sell_limit_order(amount=0.000003,price=3000)
    # api.buy_limit_order(amount=0.000003, price=3000)

    res = api.buy_limit_order(amount=0.00042277, price=3000)

    #---------------------------------------
    """
    remove this block to one functions (update_state)  !!!
    UPDATE_STATE_AFTER_BUY_SELL
    """
    data = res['_data']
    status = data['status']

    from db.connection import DBConnect
    conn = DBConnect().getConnect()

    if status != 'REJECTED':
        upd_balance(data,conn)
        upd_active_orders(data, ALGO_NAME, conn)
    if status == 'REJECTED':
        pass
        #save only in log_order

    log_orders(data,ALGO_NAME,conn)

    conn.comit()
    conn.close()
    #----------------------------------------

    res = api.cancel_order(clientOrderId='')
    #-------------------------------------
    """
    UPDATE_STATE_AFTER_CANCEL
    #res = {'ok': 'ok', '_data': {}}    
    """
    data = res['_data'] #empty
    data['clientOrderId']=clientOrderId
    data['serverCreateTimestamp'] = unix_curr_time
    data['status']='CANCELED'

    upd_balance(data, conn)
    upd_active_orders(data, ALGO_NAME, conn)
    log_orders(data, ALGO_NAME, conn)
    #------------------------------------

    res = api.order_book(clientOrderId='')
    # -------------------------------------
    """
    UPDATE_STATE_AFTER_DONE

    """
    # ------------------------------------

    #api.buy_limit_order(amount=0.00042277, price=3000)
    #save buy _order to DB  db/queriesDB.py



    #values = calculations

    #res = set (price,amount,side)

    #save res into db (transactons, curr_state)


if __name__ == '__main__':
    f_alg1(1690089409000)
