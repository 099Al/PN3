# -*- coding: utf-8 -*-

import os
import sys

import sqlite3

from configs import config


db_name = config.DB_NAME

class DBConnect:
    def getConnect(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, f'../../{db_name}')
        conn = sqlite3.connect(db_path)
        return conn

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