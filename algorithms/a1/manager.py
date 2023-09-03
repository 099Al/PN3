from configs import config
from db.queriesDB import upd_balance,upd_active_orders, log_orders,log_balance,log_orders

MODE = config.MODE
ALGO_NAME = 'A1'


def f_alg1(unix_curr_time):
    api = None
    calc_res = None

    if MODE == "TRADE":
        from api.cexioNewApi import Api


        api = Api(config.API_USER, config.API_KEY, config.API_SECRET)

        #для тестирования, чтобы перейти в нужную функция
        #В этом месте нужно ее убрать
        api.buy_limit_order()
        api.sell_limit_order()

        #set or cancel
        #save into db


    if MODE == 'TEST':
        from emulatorApi.cexioEmNewApi import emulatorApi

        api = emulatorApi('TEST_USER',unix_curr_time)

        # для тестирования, чтобы перейти в нужную функция
        # В этом месте нужно ее убрать
        api.buy_limit_order()  # Баланс im_balance меняется внутри функции. Аналогично как в реальности, после ордера меняется баланс сразу
        api.sell_limit_order()


    # CALCULATION
    # reserved вычисляется в calculation(отдельный модуль)
    # Проверка на минимум amount и есть сумма на балансе
    # После установки изменить сумму на баласе im_balance в случае TEST
    # Так же залогировать ордер
    calc_res = {'flag': 'buy', 'amount': 0.005, 'price': 26000, 'reserved': 20}  # reserved includes fee

    # if res == buy:
    #     api.buy_limit_order
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
    data = res['data']
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
    #res = {'ok': 'ok', 'data': {}}    
    """
    data = res['data'] #empty
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
