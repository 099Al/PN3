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

    # внутри делать проверку на base_min, чтобы ошибка не выходила при выставлении ордера
    # здесь же и вычислять нужную сумму для резервирования и величину комиисси после продажи
    # В реальных условиях значения комиссии могут не совпадать с расчетной, поэтому надо проверять, сверяясь с балансом
    calc_res = {'side': 'buy', 'amount': 0.005, 'price': 26000, 'reserved': 20, 'init_base':1.5,'init_quote':1000}  # reserved includes fee
    calc_res = {'side': 'sell', 'amount': 0.005, 'price': 26000, 'reserved': 0.005, 'init_base':1.5,'init_quote':1000}


    # if res == buy:
    #     api.buy_limit_order
    # if res == sell:
    #     api.sell_limit _order
    # if res == ...

    #AFTER SET ORDER
    #GET BALANCE STATUS if MODE == TRADE
    #THEN CALC RESERVED   api.account_status
    reserved = 15

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
    #data['reserved'] = reserved

    from db.connection import DBConnect
    conn = DBConnect().getConnect()

    if status != 'REJECTED':

        # Две таблицы дублируют друг друга.
        # Но для теста записываем в IM_BALANCE - эмуляция баланса
        # Для Traid режима записываем в BALANCE - для дублирования баланса на сайте, скорее всего из-за различия в комиссиях будут различия
        balance_state(data, client_side=True, algo_nm=None, conn=conn)

    if status == 'REJECTED':
        pass
        #save only in log_order

    log_orders(data,ALGO_NAME,conn)

    conn.comit()
    conn.close()
    #----------------------------------------




    res = api.cancel_order(OrderId='')  # сделать обновления в IM_BALANCE в случае теста
    #-------------------------------------
    """
    UPDATE_STATE_AFTER_CANCEL
    #res = {'ok': 'ok', 'data': {}}    
    """
    data = res['data'] #empty
    data['OrderId'] = OrderId
    data['serverCreateTimestamp'] = unix_curr_time
    data['status'] = 'CANCELED'

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
