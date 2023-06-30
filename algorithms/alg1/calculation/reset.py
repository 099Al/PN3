# -*- coding: utf-8 -*-


from algorithms.orders import  ActiveOrders, ProcessLine
from algorithms.alg1.stop.stopLine import stop_line_mark
import algorithms.alg1.stop.resetMark as stopM
from algorithms.alg1.parameters.orderParams import limit_k1,limit_k2


actOrders = ActiveOrders()
pLines = ProcessLine()

def calc_active_orders_reset(last_prices):
    reset_list = []  # список ордеров на снятие

    for id_i, order_i in actOrders.active_orders_list.items():

        d_reset_order = calc_order_reset(order_i,last_prices)

        if (d_reset_order['action'] != 'wait'):
            reset_list.append(d_reset_order)

    '''!!!!----- Сделать СОРТИРОВКУ если длина больше 1 по ПРИОРИТЕТУ в reset_list-----  !!!!'''

    return reset_list


def calc_order_reset(order,last_prices):
    id_order = order['id']
    type = order['type']
    subtype = order['subtype']
    line = pLines.findLinebyId(id_order)
    prev_price = pLines.findPrevPrice(id_order)

    #test


    '''
    #стоит ордер на продажу, если цена становиться меньше предела, то идет сброс
    и становится на продажу по цене меньшей.
    В данном условии, если что-то есть на депозите(BTC), то эта величина не продается.
    Продается, только то что есть в ордерах.
    '''

    if(type=='buy'):
        '''
        Если цена слишком ушла вверх, то Сброс
        Или по времени есть ограничение, то сброс
        '''
        #return {'action':'cancel','type':stopM.STOP_2}
        return {'action': 'wait', 'reset_type': stopM.STOP_2
                ,'id': id_order
                , 'type': type
                , 'subtype':subtype
                , 'line': line
               }




    if(type=='sell'):  # либо на депозите сумма больше X
        '''
         КОДА type==sell
         Проверка на 1-й лимит.Если ниже 1-го, но выше 2-го
         то сбрасывается и попытка продать по цене выше текущей. Но ниже 1-го лимита!!! Иначе этот ордер не сработает
         При этом last_buy_price  не меняется.  Поэтому граница 1-го и 2-го лимиту будут теми же
         
         Если вышли выше 1-го лимита, то выставляем ордер на место.
         По last_buy_price
         
         Если стала ниже 2-го предела
         Тогда надо выходть из ордера и ставить по рынку
        '''

        #Доп проверки.
        #Например на время


        '''
        Т.к. стоял ордер sell, то считаем, что был buy.
        Значит сохранились данные предыдущего сработавшего ордера.
        '''

        #Limits - границы для стопов

        '''limit_k1  сделать зависимыми от линии и prev_price'''
        '''prev_price  - здесь это предыдущая цена покупки'''

        if(prev_price is None):
            print('prev_price is None  Сделать обработку случая')

        limi1 = prev_price*(1-limit_k1)
        limit2= prev_price*(1-limit_k2)

        mark = stop_line_mark(limi1,limit2,last_prices) #положение цены относительно стопов




        if(mark=='L'): #ниже второго
            return {'action':'cancel','reset_type':stopM.STOP_2
                    , 'id': id_order
                    , 'type': type
                    , 'subtype': subtype
                    , 'line': line
                    }

        # список теукущих ордеров
        #actOrders = ActiveOrders()

       # ord_x = actOrders.findOrder(order_id)  #активный ордер
        ord_subtype = subtype


        if(mark=='B'): #между уровнями

            #ДЛЯ КАЖДОГО ID свой лимит =>  СВОЙ LIMIT_PRICE.
            #ЗДЕСЬ ЕГО НАДО ВЫВЕСТИ

            if (ord_subtype == 0):  # надо продать, но по лимитному ордеру
                return {'action':'cancel','reset_type':stopM.STOP_1
                    , 'id': id_order
                    , 'type': type
                    , 'subtype': subtype
                    , 'line': line
                    ,'limit_price':''}

            if(ord_subtype == 1):  #в прошлый раз уже был между уровнями и ордер переставили на продажу
                return {'action':'wait'}


        if(mark=='H'): #выше 1-го
            if (ord_subtype == 0):  # До лимита в прошлый раз не дошли
                return {'action':'wait'}


            '''
            Это условие лишнее.
            Т.к. вариант 1: p_sell < limit1, тогда раньше будет сделка чем возврат к старому ордеру
            вариант 2: p_sell > limit1, тогда ордер не сработает, т.к. будет снят при  p> limit1.  
            '''
            if(ord_subtype == 1):  #в прошлый раз уже был между уровнями и теперь надо вернуться к старому ордеру
                return {'action':'cancel','reset_type':stopM.R_3
                    , 'id': id_order
                    , 'type': type
                    , 'subtype': subtype
                    , 'line': line
                        }

        '''
        Условие, когда было резкое снижение цены.
        Т.е p<limit2<limit3 ,  Тогда делаем wait. И StopLoss на данный ордер не будет работать.
        '''


    return {'action':'wait'}


if __name__ == '__main__':
    calc_order_reset()





