# -*- coding: utf-8 -*-

# import db.connection as cn
import time

from algorithms.orders import ActiveOrders
from perfomance.balance.balance import DepoBalance

'''
Словарь устанвленных ордеров
Последовательность купли/продажи

структура ордера order ={'id':id,'amount':amount,'price':price,'ord_time':ord_time, 'type': r_act, 'x':x_reserv}
структура словаря order_list  = {id: order}
'''

active_orders = ActiveOrders()  # активные ордера


# очистка таблицы логов
def clear_log(conn):
    cursor = conn.cursor()
    cursor.execute('delete from transaction_log')
    conn.commit()
    cursor.close()


# логирование
def log_action(conn, line, order_values, action, market):
    id = order_values['id']
    order_time = order_values['ord_time']  # время действия по тестовым данным. В реальном времени будет присвоено значение time()
    values = ''



    deposit = DepoBalance()

    if (action == 'buy'):
        amount = order_values['amount']
        price = order_values['price']
        #type = order_values['type']  # type :   sell,buy
        mtype = order_values['mtype']  # market/limit
        x = order_values['x']  # в случае buy- сумма,которая резервируется, sold- которая поступает
        base, quote = market.split("/")

        # action : set, reset, done(sell/buy get fee)

        values = {
            'real_time': int(time.time())
            , 'id': id
            , 'tik_done': None
            , 'order_time': order_time
            , 'type': action
            , 'mtype':mtype
            , 'base': base
            , 'quote': quote
            , 'amount': amount
            , 'price': price
            , 'fee': None
            , 'change_base': None
            , 'change_quote': -x
            , 'line': line
            , 'total_base': None
            , 'total_quote': None
        }


    if (action == 'sell'):
        amount = order_values['amount']
        price = order_values['price']
        #type = order_values['type']  # type :   sell,buy
        mtype = order_values['mtype']  # market/limit
        x = order_values['x']  # в случае buy- сумма,которая резервируется, sold- которая поступает
        base, quote = market.split("/")

        values = {
            'real_time': int(time.time())
            , 'id': id
            , 'tik_done': None
            , 'order_time': order_time
            , 'type': action
            , 'mtype': mtype
            , 'base': base
            , 'quote': quote
            , 'amount': amount
            , 'price': price
            , 'fee': None
            , 'change_base': -amount
            , 'change_quote': None
            , 'line': line
            , 'total_base': None
            , 'total_quote': None
        }

    if (action == 'bought'):
        amount = order_values['amount']
        price = order_values['price']
        tik_id = order_values['tik_id']
        date_id = order_values['date_id']
        x = order_values['x']  # в случае buy- сумма,которая резервируется, sold- которая поступает
        base, quote = market.split("/")
        balance_b = deposit.totalBlnc(base)
        balance_q = deposit.totalBlnc(quote)

        values = {
            'real_time': int(time.time())
            , 'id': id
            , 'tik_done': tik_id
            , 'order_time': date_id  # время, когда сработал
            , 'type': action
            , 'mtype': None
            , 'base': base
            , 'quote': quote
            , 'amount': amount
            , 'price': price
            , 'fee': None
            , 'change_base': None
            , 'change_quote': -x
            , 'line': line
            , 'total_base': balance_b
            , 'total_quote': balance_q
        }

    if (action == 'sold'):
        amount = order_values['amount']
        price = order_values['price']
        tik_id = order_values['tik_id']
        date_id = order_values['date_id']
        x = order_values['x']  # в случае buy- сумма,которая резервируется, sold- которая поступает
        base, quote = market.split("/")
        balance_b = deposit.totalBlnc(base)
        balance_q = deposit.totalBlnc(quote)

        values = {
            'real_time': int(time.time())
            , 'id': id
            , 'tik_done': tik_id
            , 'order_time': date_id  # время, когда сработал
            , 'type': action
            , 'mtype': None
            , 'base': base
            , 'quote': quote
            , 'amount': amount
            , 'price': price
            , 'fee': None
            , 'change_base': None
            , 'change_quote': x
            , 'line': line
            , 'total_base': balance_b
            , 'total_quote': balance_q
        }

    if (action == 'cancel'):
        amount = order_values['amount']
        price = order_values['price']
        reset_time = order_values['reset_time']

        x = order_values['x']  # в случае buy- сумма,которая резервируется, sold- которая поступает
        base, quote = market.split("/")


        values = {
            'real_time': int(time.time())
            , 'id': id
            , 'tik_done': None
            , 'order_time': reset_time  # время, когда отменили
            , 'type': action
            , 'mtype': None
            , 'base': base
            , 'quote': quote
            , 'amount': amount
            , 'price': price
            , 'fee': None
            , 'change_base': None
            , 'change_quote': x
            , 'line': line
            , 'total_base': None
            , 'total_quote': None
        }



    ins_query = 'INSERT INTO transaction_log (real_time,id,tik_done,order_time,type,mtype,base,quote,amount,price,fee,change_base,change_quote,line,total_base,total_quote) ' \
                'VALUES(' \
                ':real_time' \
                ',:id' \
                ',:tik_done' \
                ',:order_time' \
                ',:type' \
                ',:mtype' \
                ',:base' \
                ',:quote' \
                ',:amount' \
                ',:price' \
                ',:fee' \
                ',:change_base' \
                ',:change_quote' \
                ',:line' \
                ',:total_base' \
                ',:total_quote' \
                ');'


    # conn = cn.getConnect()
    cursor = conn.cursor()
    try:
        cursor.execute(ins_query, values)
        conn.commit()
    except:
        from util.util_datetime import unix_to_date
        print('except:', 'id=', id, 'type=',type)
    finally:
        cursor.close()
        # conn.close()


if __name__ == '__main__':
    from db.connection import DBConnect
    dbconn = DBConnect()
    conn = dbconn.getConnect()
    cursor = conn.cursor()
    ins_query = 'INSERT INTO transaction_log (real_time,id,tik_done,order_time,type,mtype,base,quote,amount,price,fee,change_base,change_quote,line,total_base,total_quote) ' \
                'VALUES(' \
                ':real_time' \
                ',:id' \
                ',:tik_done' \
                ',:order_time' \
                ',:type' \
                ',:mtype' \
                ',:base' \
                ',:quote' \
                ',:amount' \
                ',:price' \
                ',:fee' \
                ',:change_base' \
                ',:change_quote' \
                ',:line' \
                ',:total_base' \
                ',:total_quote' \
                ');'

    values= {'real_time': 1591251677, 'id': 1591251639, 'tik_done': None, 'order_time': 1549181237,
                    'type': 'buy', 'mtype': 'limit', 'base': 'BTC', 'quote': 'USD', 'amount': 0.0227767,
                    'price': 3503.58, 'fee': None, 'change_base': None, 'change_quote': -80, 'line': 1,
                    'total_base': None, 'total_quote': None}

    cursor.execute(ins_query, values)



