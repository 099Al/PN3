from datetime import datetime

from perfomance.cache.cacheData import DBValues


import configparser

conf_data = configparser.ConfigParser()
conf_data.read('../configs/config.ini')
cex_history_tbl = conf_data['SRC']['SRC_HISTORY']
queriesIm




def hist_last_tik(cursor):
    sql = "SELECT MAX(tid) FROM " + cex_history_tbl
    res = cursor.execute(sql)
    m_tik = res.fetchall()[0][0]

    if m_tik == None:
        m_tik = 0

    return m_tik


def save_history_tik(newTiks):


    from db.connection import DBConnect
    conn = DBConnect().getConnect()
    cursor = conn.cursor()

    DBValues.last_history_tik = 1000

    return

    curr = connect.cursor()
    for x in newTiks:
        res = [(x['tid'],x['type'],x['date'],datetime.fromtimestamp(x['date']),x['amount'],x['price'])]
        curr.executemany("INSERT INTO cex_history_tik (tid,type,unixdate,date,amount,price) VALUES (?,?,?,?,?,?)",res)
    connect.commit()

    conn.close()