# -*- coding: utf-8 -*-

'''Функции для расчета изменения  различных величин после купли затем продажи или продажи затем купли'''


import numpy as np

from functions.trade import sellBTC,presellBTC,maxBTC,priceForBuyBTC,X_for_buyBTC,priceForSellBTC
from configs.config import MAKER_TAKER, TAKER


#Изменение BTC при изменении цены от текущей, до ожидаемой
def deltaBTC(btc0,current_price,expected_price,commis=0):

    '''
    :param btc0: количество BTC на балансе
    :param current_price:  если продать по данной цене (например текущая)
    :param expected_price: затем купить по этой цене
    :param commis:        комиссия при транзакциях. По умолчанию берется средняя. Можно рассчитать случай по текущей цене тогда комиссию надо брать максимальной по taker
    :return:      возвращает изменение BTC на балансе
          так же расчитывает какое кол-во BTC теряется
    '''


    if(commis == 0):
        commis = mk_tk

    btc1 = presellBTC(btc0,current_price)
    dbtc = btc0-btc1  # остаток  на балансе
    x = sellBTC(btc0,current_price,commis)['x']    # получаем после продажи
    btc = maxBTC(x,expected_price)                 # после покупки по новой цене

    return {'delta':btc-btc0+dbtc, 'btc': btc}

#   btc0,  deltaBTC  =>   deltaBTC/btc0  - процент изменения


#Изменение X при изменении цены
#если взять btc по текущей цене
def deltaX(x0,current_price,expected_price,commis):

    btc1 = maxBTC(x0, current_price)
    x1 = X_for_buyBTC(btc1,current_price,commis)

    #dx = x0 - x1 >0  # если комиссия меньше taker, то от x0 что-то должно остаться

    x2 = sellBTC(btc1,expected_price,commis)['x']    #после продажи btc

    #dX = x2-x0+dx = x2-x0+(x0-x1) = x2-x1
    return {'dx':np.round(x2-x1,2),'x2':x2}





#Необходимая цена,для получения btc
def priceForExpectBTC(btc0, current_price, btc_expected,commis=0):

    '''
    Для получения btc_expected ждем, чтобы цена уменьшилась
    :param btc0: данное кол-во.
    :param current_price:  текущая цена, по котрой продаем (возможно плюс некоторый процент к цене, чтобы комиссия была по maker)
    :param btc_expected:   желаемое кол-во BTC
    :param commis:  комиссия
    '''

    if (commis == 0):
        commis = TAKER

    x = sellBTC(btc0,current_price,commis)['x'] # получаем X при продаже

    p = priceForBuyBTC(btc_expected, x)

    return {'price',p,'x',x}



def priceForExpectX(x0,current_price,x_expected,commis):
    '''
    :param x0:  данно кол-во X, на которое покупается btc по текущей цене
    :param current_price:  текущая цена
    :param x_expected:  ожидаемое кол-во X_exp
    :param commis:      комиссия при транзакциях
    :return:
    '''
    btc1 = maxBTC(x0, current_price)
    x1 = X_for_buyBTC(btc1,current_price,commis)  #потратилось
    dx = x0-x1

    x_exp2 = x_expected-dx # т.к. на остатке, что-то останется, то необходимое кол-во X при продаже может быть меньше

    #Необходимая цена
    price_exp = priceForSellBTC(x_exp2,btc1,commis) # продажа имеющихся btc

    return {'price':price_exp['price'],'maxbtc':btc1,'sellbtc':price_exp['btc']}




if __name__ == '__main__':
    a= deltaX(476.19,9800,10300)['dx']
    print(a)


