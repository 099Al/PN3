# -*- coding: utf-8 -*-

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



