# -*- coding: utf-8 -*-
import glob
import os
import json
import configparser

from dateutil.parser import parser

from PN3.db.connection import DBConnect
from PN3.util.util_datetime import unix_to_date

conf_data = configparser.ConfigParser()
conf_data.read('../configs/config.ini')
cex_history_tbl = conf_data['DB']['HISTORY_TABLE'] #'im_cex_history_tik' #Таблица с данными для эмуляции


'''
!!! В названии фала должна быть дата формирования в формате yyyymmdd
!!! Фильтр на дату подается в формате yyyymmdd
'''

date_slice = slice(0,8)   #Часть файла с датой формирования

def save_cex_history_seq(folder_path, new_date=0):
    '''
    Загрузка данных (tik) из текстовых файлов.
    Файлы должны подаваться в последовательности как были сформированы (т.к. пропущенные промежутки(файлы) не вставятся)

    Данный приходят в формате json

    [{},{},{},...]

    '''

    cex_files = glob.glob(folder_path+"\*.txt")
    new_cex_files = [x for x in cex_files if int(os.path.basename(x)[date_slice])>=int(new_date)]

    dbconn = DBConnect()
    conn = dbconn.getConnect()
    cur = conn.cursor()

    for f in new_cex_files:
        jsfile = open(f)
        data = json.loads(jsfile.read())    #Текст в файле воспринимается как текст. Его надо распарсить как JSON, чтобы получить массив
        res = cur.execute(f"SELECT MAX(tid) FROM {cex_history_tbl}");
        max_tid = res.fetchone()[0];
        if(max_tid == None):
            max_tid = 0
        res = [(x['tid'],x['type'],x['date'],unix_to_date(x['date']),x['amount'],x['price']) for x in data if int(x['tid']) > max_tid]
        cur.executemany(f"INSERT INTO {cex_history_tbl} (tid,type,unixdate,date,amount,price) VALUES (?,?,?,?,?,?)",res)
        conn.commit()
    dbconn.closeConnect(conn)



def save_cex_history_add_json(folder_path, new_date=0):
    """
        Загрузка данных из файлов в указанной директории
        Перед вставкой проеверяется есть ли такой tik в базе

        Данный в файле приходят в виде строк словарей:

        [{},{},{},...]
        """
    cex_files = glob.glob(folder_path+"\*.txt")
    new_cex_files = [x for x in cex_files if int(os.path.basename(x)[date_slice])>=int(new_date)]

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



def save_cex_history_add(folder_path, new_date=0):
    """
    Загрузка данных из файлов в указанной директории
    Перед вставкой проеверяется есть ли такой tik в базе

    Данный в файле приходят в виде строк словарей:

    {...,}
    {...,}
    {...,}
    """
    #Список файлов в директории
    cex_files = glob.glob(folder_path+"\*.txt")

    new_cex_files = [x for x in cex_files if int(os.path.basename(x)[date_slice])>=int(new_date)]

    dbconn = DBConnect()
    conn = dbconn.getConnect()
    cur = conn.cursor()


    for hist_file in new_cex_files:

        with open(hist_file,'r') as fhist:
            lines = fhist.readlines()

            data=[]
            for line in lines:
                x = json.loads(line)
                line_x = ((x['tid'], x['type'], x['date'], unix_to_date(x['date']), x['amount'], x['price']))
                data.append(line_x)

            cur.execute("DELETE FROM stg_cex_history_tik")
            cur.executemany("INSERT INTO stg_cex_history_tik (tid,type,unixdate,date,amount,price) VALUES (?,?,?,?,?,?)",data)
            cur.execute(f"INSERT OR IGNORE INTO {cex_history_tbl} SELECT DISTINCT * FROM stg_cex_history_tik")
            conn.commit()
    dbconn.closeConnect(conn)





if __name__ == '__main__':


    cur_path = os.getcwd()
    print(cur_path)
    path_to_hist_src_data = f'{cur_path}\src_data'


    #parent_dir = os.path.dirname(cur_path)
    #pth = os.path.join(parent_dir,'src')
    #save_cex_history_seq(path_to_hist_src_data,20190224)
    #print('-',pth)
    save_cex_history_add(path_to_hist_src_data,20200702)