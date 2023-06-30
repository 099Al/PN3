# -*- coding: utf-8 -*-

'''Получение новых данных'''

from util.util_datetime import unix_to_date


cex_history_tbl= 'im_cex_history_tik'
'''
#Таблица с данными для эмуляции
# cex_history_tbl - таблица, в которой сохраняются полученные данные
# stg_cex_history_tbl - таблица, в которой сохраняется часть полученных данныыыых. 
# Для расчета.
'''

#Получение данных с cex.io
def f_data_tic():
    pass


# имитация получения данных с CEX
# Получение 1000 последних тиков на заданную дату
def f_data_tic_imitation(connect, datetm):
    # WHERE unixdate - дата в формате unixdate
    curr = connect.cursor()

    # Получение 1000 последних тиков на заданную дату
    sql = "WITH t " \
          "as (" \
          "SELECT MAX(tid) m_tid " \
          "FROM "+cex_history_tbl+" " \
          "WHERE unixdate <= '{dt}'" \
          ") " \
          "SELECT tid,type,unixdate,amount,price " \
          "FROM "+cex_history_tbl+" " \
          "WHERE tid <= (select m_tid from t) " \
          "AND tid > (select m_tid from t)-1000 " \
          "ORDER BY tid desc "

    sql = sql.format(dt=datetm)

    sql_fast = "SELECT tid,type,unixdate,amount,price " \
               "FROM "+cex_history_tbl+" " \
               "WHERE  date < '{dt}' " \
               "limit 1000 ORDER BY tid desc"
    sql_fast = sql_fast.format(dt=datetm)

    r = curr.execute(sql)
    res = r.fetchall()

    #Преобразование результата. Чтобы данные выдавались как после запроса к CEX.
    res_dict = [dict(zip(('tid','type','date','amount','price'),x)) for x in res]

    return res_dict


# Поиск последнего tid в таблице с историей tik
def his_last_tik(connect):
    curr = connect.cursor()
    sql = "SELECT MAX(tid) FROM "+cex_history_tbl
    res = curr.execute(sql)
    m_tik = res.fetchall()[0][0]

    if m_tik == None:
        m_tik=0

    return m_tik

#Новые данные в массиве
def find_new_tiks(tik_list, h_last_tik):
    f = filter(lambda x: x[0] > h_last_tik, tik_list)
    return list(f)




#В модуле с рассчетами, чтобы не выносить класс TikQueue
def push_tik():
    pass

#Удаление данных из таблицы
def clear_history(connect,tbl):
    curr = connect.cursor()
    curr.execute("DELETE FROM {table}".format(table=tbl))
    connect.commit()

def save_history_tik(connect,newTiks):

    curr = connect.cursor()
    for x in newTiks:
        res = [(x['tid'],x['type'],x['date'],unix_to_date(x['date']),x['amount'],x['price'])]
        curr.executemany("INSERT INTO cex_history_tik (tid,type,unixdate,date,amount,price) VALUES (?,?,?,?,?,?)",res)
    connect.commit()



if __name__ == '__main__':
    import db.connection as dbconn
    conn = dbconn.getConnect()
    r = f_data_tic_imitation(conn, '2019-02-02 11:05:17')


    dbconn.closeConnect(conn)
