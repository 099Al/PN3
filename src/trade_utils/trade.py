# -*- coding: utf-8 -*-
"""
Функции для расчета транзакций (покупки/продажи)
"""
from decimal import Decimal, ROUND_UP

import numpy as np
import math


from src.trade_parameters import TradeConfig

MAKER_TAKER = TradeConfig.MAKER_TAKER
BUY_FEE = TradeConfig.BUY_FEE
SELL_FEE = TradeConfig.SELL_FEE

"""
Версии функций для расчета
Возможно их надо вынести в config

Для расчета X для покупкт BTC наиболее верный результат выдает X_for_buyBTC_v3

Для расчета максимольного BTC для заданного X наиболее верно высчитывает buy_maxBTC_v3
buy_maxBTC_v1 тоже верно высчитывает, при использовании X_for_buyBTC_v3

"""
BUYBTC_VERSION=3
X_FOR_BUY_VERSION = 3

#Оставить n знаков после запятой
def cutX(x,n):
    s = str(x)
    x = s[0:s.index('.')+n+1]  # оставить только n знаков после ,
    return float(x)



#Покупка BTC
#сумма списания X при покупке заданного кол-ва BTC
def X_for_buyBTC_v1(btc,price,comiss=None):
    # comis = 0.25%
    # mk_tk_comiss - maker taker commission

    if comiss is None:
        comiss = BUY_FEE

    a = math.ceil(btc * price * 100) / 100  # сумма при покупке по цене P (без комиссии)  Округление вверх до двух знаков
    k = math.ceil((a * comiss/100) * 100) / 100
    x = a + k  # сумма, необходимая для покупки BTC (с учетом комиссии)
    x = int(x*100)/100
    return x

def X_for_buyBTC_v3(btc,price,comiss=None):
    # comis = 0.25%
    # mk_tk_comiss - maker taker commission

    btc_d = Decimal(str(btc))
    price_d = Decimal(str(price))

    if comiss is None:
        comiss = BUY_FEE

    comiss_d = Decimal(str(comiss))

    x = btc_d * price_d / (Decimal("1") - comiss_d / Decimal("100"))
    x = x.quantize(Decimal("0.01"), rounding=ROUND_UP)
    return x

def X_for_buyBTC(btc,price,comiss=None):
    if X_FOR_BUY_VERSION == 1:
        x = X_for_buyBTC_v1(btc,price,comiss)
    elif X_FOR_BUY_VERSION == 3:
        x = X_for_buyBTC_v3(btc,price,comiss)

    return x


# max BTC, которое можно взять, если на балансе X
def buy_maxBTC_v1(X, price, comiss=None):
    if comiss is None:
        comiss = BUY_FEE

    # Расположение на координатной оси
    #  Xl------X--------Xr
    #  Bl------B0-------Br

    #taker_comis=0.25%
    Br = X/(price*(1+comiss/100))
    Br = cutX(Br,8)   # максимально возможная величина (не достигается из-за округлений)
    Xr = X_for_buyBTC(Br,price,comiss)

    if(Xr<=X):   #если после округлений, суммы на балансе хватает
        return Br

    Bl = cutX(Br,6)   # отбрасывание 2-х знаков.
    #Для более быстрых расчетов надо остальную часть откинуть и выводить найденное Bl
    # return Bl

    Xl = X_for_buyBTC(Bl,price,comiss)
    while(Xl>X):                           # левая граница должна быть меньше чем есть на балансе
        Bl = Bl - 0.000001
        Xl = X_for_buyBTC(Bl,price,comiss)

    #когда Bl и Br определены ищется B0 (максимально возможный)

    # т.к. B - записывается до 8-ми знаков, то Br-Bl > 0.00000001
    # Можно было делать услови X-Xn<0.01
    # , но тогда Bl мог бы получиться больше чем 8-ю знаками
    Bn_prev = -1
    Bn = 0
    while(Br-Bl > 0.00000001):

        Bn = int((Bl+Br)*100000000/2)/100000000

        if(Bn==Bn_prev):
            return Bl

        Xn = X_for_buyBTC(Bn,price,comiss)

        if(Xn<=X):
            Bl = Bn
        else:
            Br = Bn

        Bn_prev = Bn

    return Bl

# max BTC, которое можно взять, если на балансе X. Грубой приблежение, но быстрее считается
def buy_maxBTC_v2(X,price,comiss=None):
    if comiss is None:
        comiss = BUY_FEE

    # Расположение на координатной оси
    #  Xl------X--------Xr
    #  Bl------B0-------Br

    #taker_comis=0.25%
    Br = X/(price*(1+comiss/100))
    Br = cutX(Br,8)   # максимально возможная величина (не достигается из-за округлений)
    Xr = X_for_buyBTC(Br,price,comiss)

    if(Xr<=X):   #если после округлений, суммы на балансе хватает
        return Br

    Bl = cutX(Br,6)   # отбрасывание 2-х знаков.
    return Bl






#Величина получается больше, чем при maxBTC. Так же ордер может выставиться
#Но по обраьной формуле X_for_buyBTC величина X будет больше
def buy_maxBTC_v3(X,price,comiss=None):
    if comiss is None:
        comiss = BUY_FEE
    btc = (1-comiss/100)*X/price
    return cutX(btc,8)


def buyBTC(x, price, comiss=None):
    #comiss = 0.18513 #Примерная комиссия, по которой резервируется сумма
    if comiss is None:
        comiss = BUY_FEE



    btc = None
    if BUYBTC_VERSION == 1:
        btc = buy_maxBTC_v1(x, price, comiss)
    elif BUYBTC_VERSION == 2:
        btc = buy_maxBTC_v2(x, price, comiss)
    elif BUYBTC_VERSION == 3:
        btc = buy_maxBTC_v3(x, price, comiss)

    return btc

#------------------------покупка BTC------------------------------------


#----Продажа BTC---------------------------------------------------------------
#Рассчет суммы, которая полностью продастся без округления
#Есть вариант, что выставленная сумма при продаже округлится в меньшую сторону и именно эта величина будет умножаться на цену.
def presellBTC(btc, price):
    x = btc*price
    x = cutX(x, 2)
    btc = x/price
    btc = math.ceil(btc * 100000000) / 100000000
    return btc

#btc надо предрасчитывать, чтобы часть не терялась при округлении
def sellBTC(btc,price,comiss=None):
    #x - сколько в итоге получили
    #comis - комиссия
    if comiss is None:
        comiss = SELL_FEE
    btc0 = presellBTC(btc, price)
    x = cutX(btc0*price,2)
    comis_r = np.round(comiss/100*x,2)
    x = cutX(x-comis_r,2)
    return {'x':x,'comis':comis_r}

#----------продажа BTC--------------------



#Есть X, необходимо взять BTC. Какая нужна цена (до какой величины снизится, чтобы было можно взять)
#----------------------------------------------------------
def price_for_buy_btc(btc_expected, X, comiss=None):
    '''
        X вычисляется по формуле:
        fO(x) = округление_в_большую_сторону_до_2_знаков(x)
        k-комиссия при транзакции (taker)
        X = fO(p*b) + fO(fO(p*b)*k)
        Округление можно заменит на добавление необходимой величины:
        X = p*b+e + (p*b+e)*k+w = (1+k)p*b+e+w+k*e
        где e - необходимая величина, чтобы произведение p*b округлить до двух знаков после запятой
        (пример p*b = 3.910000001  e=0.009999999  =>  p*b+e = 3.92  )
        верхняя грань e=0.01, w=0.01, k*e=0.01*0.0025=0.000025 (заменим на 0.0001)

        p = (X-e-w-k*e)/(b*(1+k))   - искомая цена

        p_r = (X)/(b*(1+k)) > p            (правая граница)
        p_l =  (X-0.01-0.01-0.0001)/(b*(1+k)) < p   (левая граница)

        '''


    '''Комиссия берется максимальной, т.к. на определенной кол-во X по цене P
       можно взять только одно значение BTC, может быть разный только остаток от X'''

    if comiss is None:
        comiss = BUY_FEE

    p_r = X / (btc_expected * (1 + comiss / 100))  # будет больше искомой
    p_l = (X - 0.0201) / (btc_expected * (1 + comiss / 100))  # будет меньше искомой

    #X_n = X_for_buyBTC(btc_expected, p_r,taker)

    while (p_r-p_l>0.01):  # т.к. X записывается до 2-х знаков после запятой
        #p_n = int((p_r + p_l) * 100 / 2) / 100
        p_n = (p_r + p_l) / 2
        X_n = X_for_buyBTC(btc_expected, p_n, comiss) # надо брать taker, т.к. по нему рассчитывается максимольно возможное BTC
        if (X_n > X):
            p_r = p_n
        else:
            p_l = p_n

       # if (p_r - p_l < 0.01):  # т.к. p записывается до 2-х знаков после запятой
       #     continue

    return cutX(p_l,2)




#Поиск btc, чтобы за имеющиеся btc, купить желаемые X
def sell_btc_for_x(x_exp, price, mk_tk=None):
    if mk_tk is None:
        mk_tk = SELL_FEE

    bl = x_exp / (price*(1-mk_tk/100))

    br = bl+0.000001
    xn = sellBTC(br,price,mk_tk)['x']

    while(xn<x_exp):
        br = br + 0.000001
        xn = sellBTC(br, price, mk_tk)['x']

    bn_prev=-1
    while (br - bl > 0.00000001):

        bn = int((bl + br) * 100000000 / 2) / 100000000

        if (bn == bn_prev):
            return presellBTC(br,price)

        bn_prev = bn

        xn = sellBTC(bn, price, mk_tk)['x']

        if(x_exp>xn):
            bl = bn
        else:
            br = bn

    return presellBTC(br,price)


#Поиск цены p, чтобы за имеющиеся btc, получить желаемые X
def price_for_sell_btc(X_exp, btc, comiss=None):

    '''
    :param X_exp: ожидаемое количество
    :param btc:   имеющееся кол-во btc
    :param comiss: комиссия при продаже
    :return:

    решение данного уравнения имеет множество решений.
    необходимо найти решение с нименьшим значением p.
    не всегда удаться продать все btc (из-за округлений).
    чем выше p, тем меньше надо btc для получения X'''

    if comiss is None:
        comiss = MAKER_TAKER

    pl = X_exp/(btc*(1-comiss/100))

    pr = pl+0.01
    xn = sellBTC(btc, pr, comiss)['x']
    while(xn<X_exp):
        pr = pr + 0.01
        xn = sellBTC(btc, pr, comiss)['x']

    pn_prev=-1
    btcn = 0
    while(pr-pl>0.001):
        pn = (pr+pl)/2
        btcn = presellBTC(btc, pr)
        xn = sellBTC(btcn, pr, comiss)['x']

        if(pn==pn_prev):
            return {'p':np.round(pr,2),'btc':btcn}

        pn_prev = pn

        if(xn>X_exp):
            pr=pn
        else:
            pl=pn

    return {'price':np.round(pr,2),'btc':btcn}





if __name__ == '__main__':
    p = 26000
    x = 15
    BUYBTC_VERSION = 3
    buy_commis = 0.18513

    btc = buyBTC(x, p, buy_commis)
    x1 = X_for_buyBTC(btc, p, buy_commis)  # перепроверка

    print('btc=', btc)
    print('x1=',x1)

    btc2 = (1 - buy_commis / 100) * x / p
    print(btc2)

    #0.00057586

    x = X_for_buyBTC_v3(btc,p,buy_commis)
    print('x',x)

    sell_btc = 0.00150000
    sell_price = 26200
    x = sellBTC(sell_btc,sell_price)
    print('sell',x)

    btc_expected = 0.000576
    x=15
    price = price_for_buy_btc(btc_expected, x)
    print('price',price)

    btc = sell_btc_for_x(15, 26200, mk_tk=None)
    print(btc)
    #x = X_for_buyBTC(b+0.0000000, p, 0.25)
    #print('x=',x)


