"""
запросы к таблицам не вида im_...
не расчетные запросы
"""
import json
from datetime import datetime

from perfomance.cache.cacheData import DBValues
from perfomance.cache.values import Transaction

from configs import config
from functions.trade import X_for_buyBTC, sellBTC

cex_history_tbl = config.DB__HISTORY_TABLE




def hist_last_tik(cursor):
    sql = "SELECT MAX(unixdate) FROM cex_history_tik"
    res = cursor.execute(sql)
    m_tik = res.fetchall()[0][0]

    if m_tik == None:
        m_tik = 0

    return m_tik

#Оставить только новые данные в массиве
def find_new_tiks(trades_list, h_last_tik):

    f = filter(lambda x: datetime.strptime(x['dateISO'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() > h_last_tik, trades_list)

    return list(f)



def save_history_tik(tiks,conn=None):


    from trade_data.db.connection import DBConnect
    conn = DBConnect().getConnect()
    cursor = conn.cursor()

    last_tik = hist_last_tik(cursor)
    #or
    #last_tik = DBValues.last_history_tik

    newTiks = find_new_tiks(tiks,last_tik)
    if not newTiks:   #empty list
        conn.close()
        return

    #Сохраняем значения
    new_last_tik_dt = max(newTiks, key= lambda x: x['dateISO'])['dateISO']
    new_last_tik = datetime.strptime(new_last_tik_dt, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
    DBValues.last_history_tik = new_last_tik

    #datetime.strptime(x['dateISO'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()


    for x in newTiks:

        sys_insert = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        res = [(x['tradeId'],x['side'],datetime.strptime(x['dateISO'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp(),x['dateISO'],x['amount'],x['price'],sys_insert)]
        cursor.executemany("INSERT INTO cex_history_tik (tid,type,unixdate,date,amount,price,sys_insert) VALUES (?,?,?,?,?,?,?)",res)
    conn.commit()

    conn.close()

def balance_state(data,client_side=True,algo_nm=None,conn=None):
    #reserved - общая зарезервированная сумма по всем ордерам
    #client_side - таблицы на стороне прогграммы, другая сторона, таблицы на стороне сайта.
    #Таблицы на стороне сайта эмулируют баланс и другие параметы, на строне клиента попытка продублировать их,
    #чтобы лишний раз не обращаться

    if client_side:
        balance_table = 'BALANCE'
        active_orders_table = 'ACTIVE_ORDERS'
    else:
        balance_table = 'IM_BALANCE'
        active_orders_table = 'IM_ACTIVE_ORDERS'

    flag_con = 0 # 1- коннект не передавался, а создался внутри функции
    if conn is None:
        flag_con = 1
        from trade_data.db.connection import DBConnect
        conn = DBConnect().getConnect()


    id = data['OrderId']
    coid = data['clientOrderId']
    status = data['status']

    unix_date = data['serverCreateTimestamp']
    date = datetime.fromtimestamp(unix_date / 1000)


    if status == 'NEW':

        side = data['side']  # buy sell
        amount = data['requestedAmountCcy1']
        price = data['price']

        currency1 = data['currency1'] #BTC
        currency2 = data['currency2']  # USD

        order_type = data['orderType']
        sys_date = datetime.now()


        cursor = conn.cursor()
        if side == 'BUY':
            reserved = X_for_buyBTC(amount, price)
            cursor.execute(f'UPDATE {balance_table} SET AMOUNT = AMOUNT - {reserved}, ifnull(RESERVED,0) = RESERVED + {reserved} WHERE CURR = {currency2}') #, (reserved,reserved,currency2))
        if side == 'SELL':
            reserved = amount
            cursor.execute(f'UPDATE {balance_table} SET AMOUNT = AMOUNT - {amount}, ifnull(RESERVED,0) = RESERVED + {amount} WHERE CURR = {currency1}') #, (amount,amount,currency1))


        values = (id, date, unix_date, currency1, currency2, side, amount, price, reserved, order_type, data, algo_nm, sys_date)
        cursor = conn.cursor()
        cursor.execute(f"""INSERT INTO {active_orders_table} (id,date,unix_date,base,quote,side,amount,price, reserved, order_type,full_traid,algo,sys_date)
                                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", values)

        cursor.commit()




    if status == 'DONE':
        #возможно надо будет добавить fee из ответа
        cursor = conn.cursor()
        res = cursor.execute(f"SELECT  AMOUNT,PRICE,SIDE,RESERVED FROM {active_orders_table} WHERE ID = ? AND STATUS = 'NEW' ",(id,))  #LOG_ORDERS
        r_amount, r_price, r_side, r_base,r_quote, reserved = res.fetchone()
        if r_side == 'BUY':
            cursor.execute(f'UPDATE {balance_table} SET  RESERVED = RESERVED-{reserved} WHERE CURR = {r_quote}')
            cursor.execute(f'UPDATE {balance_table} SET  AMOUNT = AMOUNT+{r_amount}       WHERE CURR = {r_base}')
        if r_side == 'SELL':
            cursor.execute(f'UPDATE {balance_table} SET  RESERVED = RESERVED-{reserved} WHERE CURR = {r_base}')
            res_x, comis = sellBTC(r_amount,r_price).values
            cursor.execute(f'UPDATE {balance_table} SET  AMOUNT = AMOUNT+{res_x} WHERE CURR = {r_quote}') #нужно учесть комиссия и расчитать сумму

        cursor.execute(f'DELETE FROM {active_orders_table} where id = ?', (id,))

        cursor.commit()



    if status == 'CANCELED':
        cursor = conn.cursor()
        res = cursor.execute(f"SELECT  amount,price,side,base,quote,reserved FROM {active_orders_table} WHERE ID = ? AND STATUS = 'NEW' ", (id,))  #LOG_ORDERS
        r_amount,r_price,r_side,r_base,r_quote,reserved = res.fetchone()
        if r_side == 'BUY':
            cursor.execute(f'UPDATE {balance_table} SET AMOUNT = AMOUNT+{r_amount}, ifnull(RESERVED,0) = RESERVED-{reserved} WHERE CURR = {r_quote}')
        if r_side == 'SELL':
            cursor.execute(f'UPDATE {balance_table} SET AMOUNT = AMOUNT+{r_amount}, ifnull(RESERVED,0) = RESERVED-{reserved} WHERE CURR = {r_base}')

        cursor.execute(f'DELETE FROM {active_orders_table} where id = ?', (id,))

        cursor.commit()

    if flag_con == 1:
        conn.close()


    return {'reserved':reserved}






def log_orders(data, params={}, algo_nm=None, conn=None):
    flag_con = 0  # 1- коннект не передавался, а создался внутри функции
    if conn is None:
        flag_con = 1
        from trade_data.db.connection import DBConnect
        conn = DBConnect().getConnect()


    id = data['OrderId']
    unix_date = data['serverCreateTimestamp']
    date = datetime.fromtimestamp(unix_date / 1000)
    status = data['status']
    reserved = params['reserved']
    sys_date = datetime.now()

    if status == 'NEW':
        currency1 = data['currency1']  # BTC
        currency2 = data['currency2']  # USD
        side = data['side']  # buy sell
        amount = data['requestedAmountCcy1']
        price = data['price']
        order_type = data['orderType']



        values = (id, status, side, date, unix_date, currency1, currency2, side, amount, price, reserved,order_type,data, algo_nm, sys_date)

        cursor = conn.cursor()
        cursor.execute("""INSERT INTO LOG_ORDERS (id,status,side, date,unixdate,base,quote,amount,price,reserved,order_type,full_traid,algo,sys_date)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", values)
        cursor.commit()

    if status == 'REJECTED':
        currency1 = data['currency1']  # BTC
        currency2 = data['currency2']  # USD
        side = data['side']  # buy sell
        amount = data['requestedAmountCcy1']
        price = data['price']
        order_type = data['orderType']
        reject_reason = data['orderRejectReason']

        values = (id, status, side, date, unix_date, currency1, currency2, side, amount, price, reserved, reject_reason, order_type, data, algo_nm, sys_date)

        cursor = conn.cursor()
        cursor.execute("""INSERT INTO LOG_ORDERS (id,status,side, date,unixdate,base,quote,amount,price,reserved,reject_reason, order_type,full_traid,algo,sys_date)
                                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", values)
        cursor.commit()


    if status == 'DONE' | 'CANCELED':

        sys_date = datetime.now()
        values = (id, status, date, unix_date, algo_nm, sys_date)

        cursor = conn.cursor()
        cursor.execute("""INSERT INTO LOG_ORDERS (id, status, date, unix_date, algo_nm, sys_date)
                                          VALUES (?,?,?,?,?,?)""", values)
        cursor.commit()



    conn.commit()

    if flag_con == 1:
        cursor.close()
        conn.close()


def order_done(curr_date,conn=None):
    flag_con = 0  # 1- коннект не передавался, а создался внутри функции
    if conn is None:
        flag_con = 1
        from trade_data.db.connection import DBConnect
        conn = DBConnect().getConnect()

    prev_date = curr_date - config.REQUEST_PERIOD

    cursor = conn.cursor()
    res = cursor.execute(f"""SELECT id, amount, price,reserved, side, base, quote
                                ,tid, unixdate, date
                            FROM (
                            
                            SELECT a.id, a.amount, a.price, a.reserved, a.side, a.base, a.quote
                                  ,h.tid, h.unixdate, h.date, row_number() over(partition by a.id order by h.date asc) rn
                            FROM im_active_orders a, im_cex_history_tik h 
                            WHERE {prev_date} < h.unixdate and h.unix_date <= {curr_date} 
                            and a.unix_date < h.unixdate 
                            and a.side = 'BUY' 
                            and h.side = 'SELL'
                            and a.price >= h.price 
                            ) t
                            where rn = 1""")

    done_buy_orders = res.fetchall()

    res = cursor.execute(f"""SELECT id, amount, price,reserved, side, base, quote
                                    ,tid, unixdate, date
                                FROM (

                                SELECT a.id, a.amount, a.price, a.reserved, a.side, a.base, a.quote
                                      ,h.tid, h.unixdate, h.date, row_number() over(partition by a.id order by h.date asc) rn
                                FROM im_active_orders a, im_cex_history_tik h 
                                WHERE {prev_date} < h.unixdate and h.unix_date <= {curr_date} 
                                and a.unix_date < h.unixdate 
                                and a.side = 'SELL' 
                                and h.side = 'BUY'
                                and a.price >= h.price 
                                ) t
                                where rn = 1""")

    done_sell_orders = res.fetchall()


    for row in done_buy_orders+done_sell_orders:
        id = row[0]
        cursor.execute(f'DELETE FROM im_active_orders WHERE id = {id}')


    for row in done_buy_orders+done_sell_orders:
        id, amount, price, reserved, side, base, quote, tid, unixdate, date = row
        info={}
        if side == 'BUY':
            info =\
                [{'transactionId': Transaction.transactionId+1, 'type': 'trade', 'amount': f'-{str(amount*price)}', 'details': f"Trade orderId='{id}' for user_id", 'currency': {quote}}
                ,{'transactionId': Transaction.transactionId+2, 'type': 'trade', 'amount': f'{str(amount)}', 'details': f"Trade orderId='{id}' for user_id", 'currency': {base}}
                ,{'transactionId': Transaction.transactionId+3, 'type': 'commission', 'amount': f'{amount*price-reserved}', 'details': f"Commission orderId='{id}' for user_id", 'currency': {quote}}]
            Transaction.transactionId += 3
        if side == 'SELL':
            x,fee = sellBTC(amount,price)
            info =\
                [{'transactionId': Transaction.transactionId+1, 'type': 'trade', 'amount': f'-{amount}', 'details': f"Trade orderId='{id}' for user_id", 'currency': {quote}}
                ,{'transactionId': Transaction.transactionId+2, 'type': 'trade', 'amount': f'{str(x+fee)}', 'details': f"Trade orderId='{id}' for user_id", 'currency': {base}}
                ,{'transactionId': Transaction.transactionId+3, 'type': 'commission', 'amount': f'-{fee}', 'details': f"Commission orderId='{id}' for user_id", 'currency': {quote}}]
            Transaction.transactionId += 3

        transac_info = json.dumps({info})

        values = (id, amount, price,reserved, side,tid, unixdate, date,transac_info)
        cursor.execute("""INSERT INTO LOG_ORDERS (order_id, order_amount, order_price, order_reserved, order_side, tid, unixdate, date,transac_info)
                                                  VALUES (?,?,?,?,?,?,?,?,?)""", values)




    conn.commit()

    if flag_con == 1:
        cursor.close()
        conn.close()







# def log_balance(_data,algo_nm,conn=None):
#     """
#     Возможно это логирование не нужно. Т.к. можно взять данные из log_orders
#     :param _data:
#     :param algo_nm:
#     :param conn:
#     :return:
#     """
#     flag_con = 0 # 1- коннект не передавался, а создался внутри функции
#     if conn is None:
#         flag_con = 0
#         from trade_data.connection import DBConnect
#         conn = DBConnect().getConnect()
#
#     id = _data['clientOrderId']
#     unix_date = _data['serverCreateTimestamp']
#     date = datetime.fromtimestamp(unix_date / 1000)
#     status = _data['status']
#
#     activity = ''
#     if status == 'NEW':
#         side = _data['side']  # buy sell
#         amount = _data['requestedAmountCcy1']
#         price = _data['price']
#         currency1 = _data['currency1'] #BTC
#         currency2 = _data['currency2']  # USD
#         sys_date = datetime.now()
#
#         if side == 'SELL':
#             curr = currency1
#             activity = 'RESERVED'
#             amount = amount*(-1)
#         if side == 'BUY':
#             fee = 0 #need to calc
#             curr = currency2
#             activity = 'RESERVED'
#             amount = (amount*price+fee)*(-1)
#
#
#     if status == 'DONE':
#         pass
#         #Надо поределить, как возвращается _order в статусе DONE
#         #Добавить запись в таблице
#     if status == 'CANCELED':
#         pass
#         #Надо поределить, как возвращается _order в статусе DONE
#         #Добавить запись в таблице
#
#
#
#     values(date,unix_date,curr,amount,algo_nm,id,activity,sys_date)
#
#     cursor = conn.cursor()
#     cursor.execute('INSERT INTO LOG_BALANCE (date,unix_date,curr,amount,algo_name,tid,activity,sys_date) values(?,?,?,?,?,?,?)',
#                    values)
#
#     cursor.commit()
#
#     if flag_con == 1:
#         cursor.close()
#         conn.close()




if __name__ == '__main__':

    dt = datetime.now()
    print(dt)