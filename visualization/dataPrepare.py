# -*- coding: utf-8 -*-

from db.connection import DBConnect
import re
import datetime

from util.util_datetime import unix_to_date

import time

'''
Вывод данных тиков за заданный промежуток времени
'''

dbconn = DBConnect()
conn = dbconn.getConnect()

def dateFormat(date):
    if(type==datetime.datetime):
        return 'date'
    else :
        x = str(date)
        mask_date = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        dateRegx = re.compile(mask_date, re.IGNORECASE)
        if (dateRegx.match(x)):
            return 'date'

        mask_unix = r'\d{10}'
        unixRegx = re.compile(mask_unix, re.IGNORECASE)

        if (unixRegx.match(x)):
            return 'unixdate'

        return None

def dataTiks(date_from,date_to):
    sql = 'select tid,type,amount,price,unixdate,date\n' \
          'from im_cex_history_tik\n' \
          'where {dateF}>=\'{date_from}\'\n' \
          'and {dateF}<\'{date_to}\'\n' \
          'order by tid asc'

    #Определение по какомму столбцу делать запрос. Date или unixdate
    dateF1 = dateFormat(date_from)
    dateF2 = dateFormat(date_to)

    if(dateF1!=dateF2):
        print('Форматы Дат не совпадают')
        exit()

    sql = sql.format(dateF=dateF1,date_from=date_from,date_to=date_to)

    print(sql)
    curr = conn.cursor()
    res = curr.execute(sql)

    return res






if __name__ == '__main__':





    x = int(time.time())
    date_time = datetime.datetime.fromtimestamp(1549181957)
    date_time2 = datetime.datetime.fromtimestamp(1549181957+1000)

    res = dataTiks(date_time,date_time2)
    for x in res:
        print(x)

    print('-')
    for x in res:
        print('x',x)