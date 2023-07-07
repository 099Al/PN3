# -*- coding: utf-8 -*-

import os
import sys

import sqlite3

import configparser

#from PN3.configs import config


'''
def getConnect():
    db_path = config.getPathDB()
    conn = sqlite3.connect(db_path)
    return conn


def closeConnect(connect):
    connect.close()

'''

conf_data = configparser.ConfigParser()
conf_data.read('../configs/config.ini')
db_name = conf_data['DB']['DB_NAME']


def getPathDB(dir=None):
    if dir == None:
        basedir = os.path.abspath(os.path.dirname(__file__))
    else:
        basedir = dir
    path = os.path.join(basedir, f'../{db_name}')
    print(basedir)
    return path


class DBConnect():

    conn = None

    def getConnect(self):
        if (DBConnect.conn==None):
            db_path = getPathDB()
            DBConnect.conn = sqlite3.connect(db_path)
            return DBConnect.conn
        else:
            return DBConnect.conn


    def closeConnect(self,connect):
        connect.close()


    def check_connect(self):
        conn = self.getConnect()
        query = 'select sqlite_version();'

        cursor = conn.cursor()
        res = cursor.execute(query)
        print('version:',res.fetchone()[0])
        conn.close()

if __name__ == '__main__':

    DBConnect().check_connect()

    print(conf_data['DB']['DB_NAME'])


    '''
    ins_query = 'INSERT INTO transaction_log ( id,order_time,real_time) ' \
                'VALUES(3,123,1234);'
    c =  DBConnect()

    con1 = c.getConnect()
    print(con1)
    cursor = con1.cursor()
    r = cursor.execute('SELECT max(ID) ID FROM transaction_log')
    r1 = r.fetchall()
    r2 = r1[0][0]
    print(r2)
    #con1.commit()


    con2 = c.getConnect()
    print(con2)
    ins_query2 = 'INSERT INTO transaction_log ( ID,order_time,real_time) ' \
                 'VALUES('+str(r2+1)+',123,1234);'
    cursor = con2.cursor()
    cursor.execute(ins_query2)
    #con2.commit()

    con3 = c.getConnect()
    print(con3)
    ins_query3 = 'INSERT INTO transaction_log ( ID,order_time,real_time) ' \
                 'VALUES(' + str(r2 + 2) + ',123,1234);'
    cursor = con3.cursor()
    cursor.execute(ins_query3)
    con3.commit()

    #con1.close()
    #con2.close()
    '''