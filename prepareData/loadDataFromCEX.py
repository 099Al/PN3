# -*- coding: utf-8 -*-
import glob
import os
import json

from dateutil.parser import parser

from db.connection import DBConnect

from util.util_datetime import unix_to_date


cex_history_tbl= 'im_cex_history_tik' #Таблица с данными для эмуляции

'''
Загрузка данных (tik) из текстовых файлов.
Файлы должны подаваться в последовательности как были сформированы (т.к. пропущенный промежутки(файлы) не вставятся)
Фильтр на дату в формате yyyymmdd
'''
def save_cex_history_seq(folder_path, new_date=0):


    cex_files = glob.glob(folder_path+"\*.txt")
    new_cex_files = [x for x in cex_files if int(os.path.basename(x)[4:12])>=int(new_date)]

    dbconn = DBConnect()
    conn = dbconn.getConnect()
    cur = conn.cursor()

    for f in new_cex_files:
        jsfile = open(f)
        data = json.loads(jsfile.read())    #Текст в файле воспринимается как текст. Его надо распарсить как JSON, чтобы получить массив
        res = cur.execute("SELECT MAX(tid) FROM im_cex_history_tik");
        max_tid = res.fetchone()[0];
        if(max_tid == None):
            max_tid = 0
        res = [(x['tid'],x['type'],x['date'],unix_to_date(x['date']),x['amount'],x['price']) for x in data if int(x['tid']) > max_tid]
        cur.executemany("INSERT INTO "+cex_history_tbl+" (tid,type,unixdate,date,amount,price) VALUES (?,?,?,?,?,?)",res)
        conn.commit()
    dbconn.closeConnect(conn)

#Загрузка данных (tik) из текстовых файлов.
def save_cex_history_add(folder_path, new_date=0):

    cex_files = glob.glob(folder_path+"\*.txt")
    new_cex_files = [x for x in cex_files if int(os.path.basename(x)[4:12])>=int(new_date)]

    dbconn = DBConnect()
    conn = dbconn.getConnect()
    cur = conn.cursor()

    for f in new_cex_files:
        jsfile = open(f)
        data = json.loads(jsfile.read())

        cur.execute("DELETE FROM stg_cex_history_tik")
        res = [(x['tid'],x['type'],x['date'],unix_to_date(x['date']),x['amount'],x['price']) for x in data]
        cur.executemany("INSERT INTO stg_cex_history_tik (tid,type,unixdate,date,amount,price) VALUES (?,?,?,?,?,?)",res)
        cur.execute("INSERT OR IGNORE INTO "+cex_history_tbl+" SELECT DISTINCT * FROM stg_cex_history_tik")
        conn.commit()
    dbconn.closeConnect(conn)





if __name__ == '__main__':
    pth = "D:\Alex\ProgramSpace\pythonwkspc\Projects\PN3\src"
    cur_path = os.getcwd()
    parent_dir = os.path.dirname(cur_path)
    pth = os.path.join(parent_dir,'src')
    #save_cex_history_seq(pth,20190224)
    save_cex_history_add(pth,20200702)