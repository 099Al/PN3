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