from datetime import datetime

from perfomance.cache.cacheData import DBValues

from configs import config

cex_history_tbl = config.DB__HISTORY_TABLE




def hist_last_tik(cursor):
    sql = "SELECT MAX(tid) FROM " + cex_history_tbl
    res = cursor.execute(sql)
    m_tik = res.fetchall()[0][0]

    if m_tik == None:
        m_tik = 0

    return m_tik

#Оставить только новые данные в массиве
def find_new_tiks(tik_list, h_last_tik):
    f = filter(lambda x: x['tid'] > h_last_tik, tik_list)
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

    new_last_tik = max(newTiks, key= lambda x: x['tid'])['tid']
    DBValues.last_history_tik = new_last_tik



    for x in newTiks:
        res = [(x['tid'],x['type'],x['date'],datetime.fromtimestamp(x['date']),x['amount'],x['price'])]
        cursor.executemany("INSERT INTO cex_history_tik (tid,type,unixdate,date,amount,price) VALUES (?,?,?,?,?,?)",res)
    conn.commit()

    conn.close()