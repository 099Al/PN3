# -*- coding: utf-8 -*-

'''
Переименован из db.feeslimits

Параметры комиссий за перевод, транзакции
Параметры берутся из таблиц в БД
'''
# get alfa currency
def alfa_curr(connect, X,Y):
    curs = connect.cursor()
    sql  = "SELECT BYE,SELL, DT FROM exchange " \
           "WHERE BANK = 'ALFA' and base = '{X}' and quote = '{Y}' _order by DT DESC limit 1".format(X=X,Y=Y)
    r = curs.execute(sql)
    res = r.fetchone()
    return res

# get bank currency
def bank_curr(connect,bank, X,Y):
    curs = connect.cursor()
    sql  = "SELECT BYE,SELL, DT FROM exchange " \
           "WHERE BANK = '{bank}' and base = '{X}' and quote = '{Y}' _order by DT DESC limit 1".format(X=X,Y=Y,bank=bank)
    r = curs.execute(sql)
    res = r.fetchone()
    return res

# get cex fee
def maker_taker(connect,vol30d):
    curs = connect.cursor()
    sql = "SELECT MAKER, TAKER FROM maker_taker WHERE VOL30d = {v}".format(v=vol30d)
    r = curs.execute(sql)
    res = r.fetchone()
    return res


# get deposit fee
def deposit_fee(connect,curr, method):
    curs = connect.cursor()
    sql = "SELECT DEPOSIT, DEPOSIT_FIX, WITHDRAWAL, WITHDRAWAL_FIX FROM deposit_fee " \
          "WHERE METHOD = '{MTD}' AND CURR = '{C}'".format(MTD = method, C=curr)
    #connection.row_factory = lambda cursor, row: row[0]
    r = curs.execute(sql)
    res = r.fetchone()
    return res



if __name__ == '__main__':

    import db.connection as cn

    print('Hello')
    conn = cn.getConnect()

    #rs = alfa_curr(conn,'USD','RUB')

    curs = conn.cursor()
    sql = "SELECT ID, D1, D2, D3,D4 FROM tst "
    # connection.row_factory = lambda cursor, row: row[0]
    r = curs.execute(sql)
    res = r.fetchone()
    print(res)
    print(res[2]+1)



    cn.closeConnect(conn)



