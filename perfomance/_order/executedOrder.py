# -*- coding: utf-8 -*-

from perfomance._balance.balance import DepoBalance
from algorithms.orders import ActiveOrders,ProcessLine
import perfomance._loging.logAction as log
from db.connection import DBConnect


#changeConst = changeConstants()
actOrders = ActiveOrders()  # список теукущих ордеров

deposit = DepoBalance()  # Баланс


dbconn = DBConnect()
conn = dbconn.getConnect()


def executeOrders(orders,market):

    #открыть коннект

    for order_i in orders:
        executeOneOrder(order_i,market)

    #закрыть коннект



def executeOneOrder(order, market):

    #На вход идет переменная _order {'order_id':x,'tik_id':tik_id,'date_id':date_id,'price':market_price}

    id = order['order_id']  # id сработавшего ордера
    tik_id = order['tik_id']  # tik на котором сработал ордер
    date_id = order['date_id']  # date когда сработал оредер

    doneOrd = actOrders.removeOrder(id)  # сработавший ордер.  Удаление из списка активных

    ''' Освобождаем линию и 
        записываем данные сработавшего ордера
    '''
    pLine = ProcessLine()
    line = pLine.doneOrder(doneOrd)

    # инициализация
    xc = 0
    curr = ''
    sb = ''

    ord_type = doneOrd['type']
    ord_mtype = doneOrd['mtype']
    if (ord_mtype == 'market'):  # если ордер был купить/продать по рынку
        doneOrd.update({'price': order['price']})  # то находим цену сделки

    if (ord_type == 'buy'):
        xc = doneOrd['amount']
        curr = 'BTC'
        #deposit.changeBlnc(xc, 'BTC')
        #changeConst.lastOrderFlag = 'b'  # меняем флаг ордера
        #changeConst.lastBuyPrice = doneOrd['price']  # сохраняем цену покупки   ПЕРЕНЕСЕНО В PROCESS LINE

        sb = 'bought'

    if (ord_type == 'sell'):
        xc = doneOrd['x']  # сумма, которую должны получить
        curr = 'USD'
        #deposit.changeBlnc(xc, 'USD')  # получили x на депозит
        #changeConst.lastOrderFlag = 's'  # меняем флаг ордера
        #changeConst.lastSellPrice = doneOrd['price']  # сохраняем цену продажи  ПЕРЕНЕСЕНО В PROCESS LINE

        sb = 'sold'



    doneOrd.update({'tik_id': tik_id})
    doneOrd.update({'date_id': date_id})

    deposit.changeBlnc(xc, curr)  # получили на депози    !!! эту функцию можно вынести
    # line - найти по id в словаре
    log.log_action(conn, line, doneOrd, sb , market)

    return {'xc':xc,'curr':curr}

    '''
    #РЕАЛИЗОВАТЬ 13.02.2020
    
    #Если данный ордер был выставлен по причине стопа
    #То по данному id надо в LINES найти ID_LINE и там найти id Предыдущего ордера
    
    

    #В LINES освободить Process
    '''