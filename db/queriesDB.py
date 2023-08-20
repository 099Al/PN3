"""
запросы к таблицам не вида im_...
не расчетные запросы
"""
from datetime import datetime

from perfomance.cache.cacheData import DBValues

from configs import config

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



def save_history_tik(tiks):


    from db.connection import DBConnect
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

def upd_balance(data,conn=None):
    flag_con = 0 # 1- коннект не передавался, а создался внутри функции
    if conn is None:
        flag_con = 0
        from db.connection import DBConnect
        conn = DBConnect().getConnect()

    id = data['clientOrderId']
    status = data['status']

    if status == 'NEW':

        side = data['side']  # buy sell
        amount = data['requestedAmountCcy1']
        price = data['price']
        currency1 = data['currency1'] #BTC
        currency2 = data['currency2']  # USD


        cursor = conn.cursor()
        if side == 'BUY':
            fee = 0 #ned to calculate by spaecial rules
            reserved = amount*price + fee
            cursor.execute('UPDATE BALANCE SET AMOUNT = AMOUNT-?, ifnull(RESERVED,0) = RESERVED+? WHERE CURR = ?', (reserved,reserved,currency2))
        if side == 'SELL':
            cursor.execute('UPDATE BALANCE SET AMOUNT = AMOUNT-?, ifnull(RESERVED,0) = RESERVED+? WHERE CURR = ?', (amount,amount,currency1))

        cursor.commit()

    if status == 'DONE':
        #возможно надо будет добавить fee из ответа
        cursor = conn.cursor()
        res = cursor.execute("SELECT  AMOUNT,PRICE,SIDE,= FROM LOG_ORDERS WHERE ID = ? AND STATUS = 'NEW' ",(id,))
        #found amount by id
        #update
        #cursor.commit()
        pass
    if status == 'CANCELED':
        cursor = conn.cursor()
        res = cursor.execute("SELECT  amount,price,side,base,quote,fee FROM LOG_ORDERS WHERE ID = ? AND STATUS = 'NEW' ", (id,))
        r_amount,r_price,r_side,r_base,r_quote,r_fee = res.fetchone()
        if r_side == 'BUY':
            cursor.execute('UPDATE BALANCE SET AMOUNT = AMOUNT+?, ifnull(RESERVED,0) = RESERVED-? WHERE CURR = ?',
                       (r_amount*r_price+fee, r_amount*r_price+fee, quote))
        if r_side == 'SELL':
            cursor.execute('UPDATE BALANCE SET AMOUNT = AMOUNT+?, ifnull(RESERVED,0) = RESERVED-? WHERE CURR = ?',
                       (r_amount, r_amount, base))
        cursor.commit()

    if flag_con == 1:
        cursor.close()
        conn.close()


def upd_active_orders(data, algo_nm, conn=None):
    flag_con = 0 # 1- коннект не передавался, а создался внутри функции
    if conn is None:
        flag_con = 0
        from db.connection import DBConnect
        conn = DBConnect().getConnect()

    id = data['clientOrderId']
    unix_date = data['serverCreateTimestamp']
    date = datetime.fromtimestamp(unix_date/1000)
    status = data['status']

    if status == 'NEW':

        currency1 = data['currency1']  # BTC
        currency2 = data['currency2']  # USD
        side = data['side']  # buy sell
        amount = data['requestedAmountCcy1']
        price = data['price']
        order_type = data['orderType']
        sys_date = datetime.now()

        values = (id,date,unix_date,currency1,currency2,side,amount,price,order_type,data,algo_nm,sys_date)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO ACTIVE_ORDERS (id,date,unix_date,base,quote,side,amount,price,order_type,full_traid,algo,sys_date)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",values)

        cursor.commit()



    if status == 'DONE' | 'CANCELED':
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ACTIVE_ORDERS where id = ?', (order_id,))
        cursor.commit()

    if flag_con == 1:
        conn.commit()
        conn.close()



def log_orders(data, algo_nm, conn=None):
    flag_con = 0  # 1- коннект не передавался, а создался внутри функции
    if conn is None:
        flag_con = 0
        from db.connection import DBConnect
        conn = DBConnect().getConnect()


    id = data['clientOrderId']
    unix_date = data['serverCreateTimestamp']
    date = datetime.fromtimestamp(unix_date / 1000)
    status = data['status']
    total = 0

    if status == 'NEW':
        currency1 = data['currency1']  # BTC
        currency2 = data['currency2']  # USD
        side = data['side']  # buy sell
        amount = data['requestedAmountCcy1']
        price = data['price']
        order_type = data['orderType']
        sys_date = datetime.now()

        fee = 0  #calc fee
        if side == 'BUY':
            total = amount*price+fee
        if side == 'SELL':
            total = amount

        values = (id, status, side, date, unix_date, currency1, currency2, side, amount, price, total,order_type,data, algo_nm, sys_date)

        cursor = conn.cursor()
        cursor.execute("""INSERT INTO LOG_ORDERS (id,status,side, date,unixdate,base,quote,amount,price,total,order_type,full_traid,algo,sys_date)
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

        values = (id, status, side, date, unix_date, currency1, currency2, side, amount, price, total, reject_reason, order_type, data, algo_nm,sys_date)

        cursor = conn.cursor()
        cursor.execute("""INSERT INTO LOG_ORDERS (id,status,side, date,unixdate,base,quote,amount,price,total,reject_reason, order_type,full_traid,algo,sys_date)
                                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", values)
        cursor.commit()


    if status == 'DONE':
        pass
        # Надо определить, как возвращается _order в статусе DONE
        # Добавить запись в таблице
        # values = id, status, side, date, unix_date
    if status == 'CANCELED':
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
#         from db.connection import DBConnect
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