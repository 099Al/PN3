# -*- coding: utf-8 -*-



'''Снятие ордера'''

import perfomance.loging.logAction as log
from algorithms.orders import ActiveOrders,SavedOrders,ProcessLine
from perfomance.balance.balance import DepoBalance

import algorithms.alg1.stop.resetMark as stopM

from db.connection import DBConnect

# список теукущих ордеров
actOrders = ActiveOrders()

#сохраненные ордера
savedOrders = SavedOrders()

#Линии ордеров
pLines = ProcessLine()

#Коннект
dbconn = DBConnect()
conn = dbconn.getConnect()


deposit = DepoBalance()  # Баланс


def remove_order(order_id,reason,reset_time,market='BTC/USD'):
    '''
    :param order_id:
    :param reason:    причина снятия ордера
    :param reset_time:
    :param market:
    :return:
    '''


    # API

    removed = actOrders.removeOrder(order_id)  # ордер, который сняли
    line = pLines.removeOrder(order_id)

    #Сохраняем снятый ордер
    if (reason == stopM.STOP_1):
        savedOrders.saveOrderPrmt(order_id,removed)


    removed.update({'reset_time': reset_time})
    reserved_sum = 0
    ord_type = removed['type']

    if (ord_type == 'buy'):
        reserved_sum = removed['x']  # зарезервированная сумма
        deposit.changeBlnc(reserved_sum,'USD')  # возвратили x на депозит

    if (ord_type == 'sell'):
        reserved_sum = removed['amount']
        deposit.changeBlnc(reserved_sum, 'BTC')  # возвратили x на депозит





    # line - найти по id в словаре
    log.log_action(conn, line, removed, 'cancel', market)


    return {'reserved_sum':reserved_sum,'removed_order':removed}