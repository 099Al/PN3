



def save_history_tik(connect,newTiks):

    curr = connect.cursor()
    for x in newTiks:
        res = [(x['tid'],x['type'],x['date'],unix_to_date(x['date']),x['amount'],x['price'])]
        curr.executemany("INSERT INTO cex_history_tik (tid,type,unixdate,date,amount,price) VALUES (?,?,?,?,?,?)",res)
    connect.commit()