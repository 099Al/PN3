# -*- coding: utf-8 -*-

from functions.trade import maxBTC,presellBTC,sellBTC,priceForBuyBTC,priceForSellBTC
from functions.deltas import deltaBTC,deltaX,priceForExpectBTC,priceForExpectX

# Основные функции----------
#Параметры для установки ордера на покупку
#Какой кол-во btc и по какой цене, чтобы взять на X(на всю сумму)
def infoParametersToBuyBTC(price,x):
    step = 10
    btc_n = maxBTC(x, price)
    print('BTC_max_0=', btc_n, 'price=', price)

    print('max')
    for i in range(-5,6):
        dp = i*step
        price_n = price+dp
        btc_n = maxBTC(x,price_n)
        if i==0:
            print('---btc max=',btc_n,'price=',price_n)
        else:
            print('btc max=', btc_n, 'price=', price_n)
    print('min')
#Параметры для установки ордера на продажу
def infoParametersToSellBTC(btc,price,mk_tk,taker):

    step=10

    print('Продать btc:',btc)
    btc_pre_n = presellBTC(btc, price)
    x_n = sellBTC(btc_pre_n, price, mk_tk)['x']
    print('btc_pre_0:', btc_pre_n, 'цена:', price, 'X_mt:', x_n, '%_mt', mk_tk)
    for i in range(-5,6):
        dp =  i*step
        price_n = price+dp
        btc_pre_n = presellBTC(btc,price_n)
        x_n = sellBTC(btc_pre_n,price_n,mk_tk)['x']
        x_n_taker = sellBTC(btc_pre_n,price_n,taker)['x']

        print('btc_pre:',btc_pre_n,'цена:',price_n,' X_mt:',x_n,'X_tk:',x_n_taker,'%_mt:',mk_tk,)


#-------------------------


#Изменение BTC при продаже по текущей цене и покупке по новой
def infoDeltaBTC(btc,price_to_sell,price_exp_to_buy,mk_tk,taker):


    dBTC = deltaBTC(btc,price_to_sell,price_exp_to_buy,mk_tk)
    dBTC1 = deltaBTC(btc, price_to_sell, price_exp_to_buy, taker)


    print('BTC0=',btc,'текущая цена=',price_to_sell,'ожидаемая цена',price_exp_to_buy)
    print('dBTC=',dBTC,'comiss=',mk_tk)
    print('dBTC=', dBTC1, 'comiss=', taker)


def infoDeltaX(x0,price_to_buy,price_exp_to_sell,mk_tk):


    dx = deltaX(x0,price_to_buy,price_exp_to_sell,mk_tk)['dx']
    print()
    print('x0=',x0,'Цена при покупке BTC на x0=',price_to_buy)
    print('Цена при продаже=',price_exp_to_sell)
    print('изменения dx:',dx)
    print('итого:',x0+dx)


#Продать сейчас BTC и найти цену, по которой можно получить btc_exp
def infoExpPrice_sellBTC0_buyBTC(btc0, current_price, btc_expected,commis):


    r = priceForExpectBTC(btc0, current_price, btc_expected,commis)


    print('Продать btc0:',btc0,'По цене:',current_price)
    print('Получим X:',r['x'])
    print('Купиить X по ИСКОМОЙ цене:',r['price'])
    print('Получим:',btc_expected)




#Купить BTC  на X. Найти цену, по которой продать BTC для X
def infoExpPrice_buyBTC_sellBTC(x0,current_price,x_expected,commis):


    r = priceForExpectX(x0,current_price,x_expected,commis)

    print('Есть X=',x0, 'купить на них btc=',r['maxbtc'],'по цене',r['price'])
    print('Продать btc_presell',r['sellbtc'],'получим X',x_expected)
    print('Искомая цена продажи',r['price'])



#Поиск цены для покупки BTC0
def infoExpPrice_buyBTC(X, btc_exp):


    p = priceForBuyBTC(btc_exp, X)

    print('Для покупки BTC:', btc_exp, 'На все X', X)
    print('Цена должна снизиться до', p)

def infoExpPrice_sellBTC(x_exp, btc, commis):


    # продажа имеющихся btc
    p_exp = priceForSellBTC(x_exp, btc, commis)

    print('Для получения X:',x_exp,'   за BTC=',btc)
    print('Цена продажи:',p_exp['price'],'   BTCpresell:',p_exp['sellbtc'])


#Остальные функции высчитывать на Практике


if __name__ == '__main__':

    price = 26156
    x = 20
    infoParametersToBuyBTC(price,x)