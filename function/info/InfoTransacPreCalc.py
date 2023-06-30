# -*- coding: utf-8 -*-

#Параметры для установки ордера на покупку
def infoParametersToBuyBTC(price,x):
    from  function.transacFunction import maxBTC
    step = 10
    btc_n = maxBTC(x, price)
    print('BTC_max_0=', btc_n, 'price=', price)

    for i in range(-5,6):
        dp = i*step
        price_n = price+dp
        btc_n = maxBTC(x,price_n)

        print('btc max=',btc_n,'price=',price_n)

#Параметры для установки ордера на продажу
def infoParametersToSellBTC(btc,price,mk_tk,taker):
    from function.transacFunction import presellBTC,sellBTC

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

#Изменение BTC при продаже по текущей цене и покупке по новой
def infoDeltaBTC(btc,price_to_sell,price_exp_to_buy,mk_tk,taker):

    from function.calcDeltas import deltaBTC

    dBTC = deltaBTC(btc,price_to_sell,price_exp_to_buy,mk_tk)
    dBTC1 = deltaBTC(btc, price_to_sell, price_exp_to_buy, taker)


    print('BTC0=',btc,'текущая цена=',price_to_sell,'ожидаемая цена',price_exp_to_buy)
    print('dBTC=',dBTC,'comiss=',mk_tk)
    print('dBTC=', dBTC1, 'comiss=', taker)


def infoDeltaX(x0,price_to_buy,price_exp_to_sell,mk_tk):
    from function.calcDeltas import deltaX

    dx = deltaX(x0,price_to_buy,price_exp_to_sell,mk_tk)['dx']
    print()
    print('x0=',x0,'Цена при покупке BTC на x0=',price_to_buy)
    print('Цена при продаже=',price_exp_to_sell)
    print('изменения dx:',dx)
    print('итого:',x0+dx)


#Продать сейчас BTC и найти цену, по которой можно получить btc_exp
def infoExpPrice_sellBTC0_buyBTC(btc0, current_price, btc_expected,commis):
    from function.calcDeltas import priceForExpectBTC

    r = priceForExpectBTC(btc0, current_price, btc_expected,commis)


    print('Продать btc0:',btc0,'По цене:',current_price)
    print('Получим X:',r['x'])
    print('Купиить X по ИСКОМОЙ цене:',r['price'])
    print('Получим:',btc_expected)




#Купить BTC  на X. Найти цену, по которой продать BTC для X
def infoExpPrice_buyBTC_sellBTC(x0,current_price,x_expected,commis):
    from function.calcDeltas import priceForExpectX

    r = priceForExpectX(x0,current_price,x_expected,commis)

    print('Есть X=',x0, 'купить на них btc=',r['maxbtc'],'по цене',r['price'])
    print('Продать btc_presell',r['sellbtc'],'получим X',x_expected)
    print('Искомая цена продажи',r['price'])



#Поиск цены для покупки BTC0
def infoExpPrice_buyBTC(X, btc_exp):
    from function.transacFunction import priceForBuyBTC

    p = priceForBuyBTC(btc_exp, X)

    print('Для покупки BTC:', btc_exp, 'На все X', X)
    print('Цена должна снизиться до', p)

def infoExpPrice_sellBTC(x_exp, btc, commis):
    from function.transacFunction import priceForSellBTC

    # продажа имеющихся btc
    p_exp = priceForSellBTC(x_exp, btc, commis)

    print('Для получения X:',x_exp,'   за BTC=',btc)
    print('Цена продажи:',p_exp['price'],'   BTCpresell:',p_exp['sellbtc'])


#Остальные функции высчитывать на Практике


if __name__ == '__main__':

    # Параметры
    from deposit.feeslimits.constant import mk_tk,taker
    from function.utilF import last_prices,current_price

    # Комиссии при транзакции
    mk_tk_usd = mk_tk
    mk_tk_rub = mk_tk


    # Состояние депозита
    x_usd_depo = 40
    x_rub_depo = 1945.33
    btc_depo = 0.00569347

    #Ожидаемые величины
    x_usd_exp = 1000
    x_rub_exp = 100000
    btc_exp = 1.0

    price_usd_exp = 7000
    price_rub_exp = 10000

    delta_price_usd = 0
    delta_price_rub = 0

    #Цена
    p_u_l = last_prices('BTC', 'USD', delta_price=0)
    #p_r_l = last_prices('BTC', 'RUB', delta_price=0)

    p_u_a = current_price('BTC', 'USD')['asks']  # При быстрой покупке, берем по цене, за которую  продают  комиссия taker
    #p_r_a = current_price('BTC', 'RUB')['asks']  # При быстрой покупке, берем по цене, за которую  продают

    p_u_b = current_price('BTC', 'USD')['bids']  # При быстрой покупке, берем по цене, за которую  продают  комиссия taker
    #p_r_b = current_price('BTC', 'RUB')['bids']  # При быстрой покупке, берем по цене, за которую  продают

    p_u=30000
    #p_r=488148.0
    p_exp = 9818

    print('Цена для расчета:', p_u, 'usd', 'last:', p_u_l, 'asks', p_u_a, 'bids', p_u_b, 'delta:', p_u_a - p_u_b)
    #print('Цена для расчета:', p_r, 'usd', 'last:', p_r_l, 'asks', p_r_a, 'bids', p_r_b, 'delta:', p_r_a - p_r_b)


    #Класс для подсчета информаци
    #cl_fromDep = InfoPreCalcTransac()

    infoParametersToBuyBTC(29400, 60)
    #infoParametersToBuyBTC(p_u,x_usd_depo) #Покупка BTC на USD. Шаг = 10
    #infoParametersToBuyBTC(p_r, x_rub_depo)  # Покупка BTC на USD. Шаг = 10
    #infoParametersToSellBTC(btc_depo, p_u, mk_tk,taker) # Продажа BTC за USD. Шаг=10
    #infoParametersToSellBTC(0.002635, 9300, mk_tk, taker)  # Продажа BTC за USD. Шаг=10

    #Дельты
    # x_usd_depo = 30
    #infoDeltaBTC(btc_depo, p_u_a, price_exp_to_buy, mk_tk, taker)
    #infoExpPrice_sellBTC0_buyBTC(btc0, current_price, btc_expected,commis)
    #infoExpPrice_buyBTC_sellBTC(x0,current_price,x_expected,commis)
    #infoDeltaX(x_usd_depo,8500,9800,mk_tk)

    #infoExpPrice_sellBTC0_buyBTC(0.00133, 30000, 45500, 0.1)

    #Поиск цены
    #x= 50
    #infoExpPrice_buyBTC(x,btc_exp)
    #infoExpPrice_sellBTC(x_exp, btc, commis)