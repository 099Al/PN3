# -*- coding: utf-8 -*-

'''Установка ордера'''
import time

import perfomance.loging.logAction as log
from algorithms.orders import ActiveOrders
from perfomance.balance.balance import DepoBalance

from db.connection import DBConnect



'''УСТАНОВКА ОРДЕРА'''

# список теукущих ордеров
actOrders = ActiveOrders()

#Коннект
dbconn = DBConnect()
conn = dbconn.getConnect()

#Баланс
deposit = DepoBalance()  # Баланс

def placeOrder(line,order,subtype,ord_time,market='BTC/USD'):


    '''При установке по limit. API возвращает ответ в виде
    {
        "complete": false,
        "id": "89067468",
        "time": 1512054972480,
        "pending": "12.00000000",
        "amount": "12.00000000",
        "type": "buy",
        "price": "1155.67"
    }
    '''
    type = order['type']
    amount = order['amount']  # количество
    price = order['price']  # по какой цене
    reserv = order['x']
    mtype = order['mtype']  # market limit



    # установка ордера через API
    if(mtype=='limit'):
        if (type=='buy'):
            pass
            #PRIVATE API place_order = api.buy_limit_order(amount,price,market)  # На выходе получается словарь с данными ордера
        if(type=='sell'):
            pass
            # PRIVATE API place_order = api.sell_limit_order(amount,price,market)  # На выходе получается словарь с данными ордера

    if (mtype == 'market'):
        if (type == 'buy'):
            pass
            # PRIVATE API place_order = api.open_long_position(...)
            # long position позволяет ставить STOPLOSS
        if (type == 'sell'):
            pass


    # Для расчетов генерация id.
    # В рабочем режиме  id берется из ответа place_order = Api.id
    id = int(time.time())

    #Для ord_time при тестировании записываем значение current_time, которое передается в функцию
    #Это значение должно быть равно времени установки ордера по тестовым данным
    # В рабочем режиме, это время должно быть взято из place_order(текущее время)
    # НЕОБХОДИМО СРАВНИТЬ ФОРМАТ
    #ord_time = ord_time

    #Параметры ордера, которые  будут сохраняться, для рассчетов
    place_order = {'id': id,
                   'amount': amount,
                   'price': price,
                   'ord_time': ord_time,
                   'type': type,            #sell,buy
                   'subtype':subtype,        #0-normal, 1-stoploss   - тип ордера
                   'mtype': mtype,           #limit, market
                   'x': reserv}

    #активные ордера
    actOrders.addOrder(place_order['id'], place_order)

    if(type=='sell'):
        deposit.changeBlnc(-reserv, 'BTC')
    if(type=='buy'):
        deposit.changeBlnc(-reserv, 'USD')

    #Логирование ордера
    #log.log_action(conn,line, place_order,type, market)
    # !!!!!!!ДОБАВИТЬ ТИП ОРДЕРА В algParams

    return {'place_order':place_order}