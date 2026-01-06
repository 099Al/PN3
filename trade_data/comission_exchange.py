# -*- coding: utf-8 -*-

'''
Переименован из trade_data._feeslimits

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





if __name__ == '__main__':

    import trade_data.db.connection as cn

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



