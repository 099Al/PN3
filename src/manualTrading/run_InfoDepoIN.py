# -*- coding: utf-8 -*-


import numpy as np

from src.api.provider import ApiProvider
from src.precalculation.info_deposit_in import InfoCalcToDep
from src.trade_parameters import TradeConfig




def info_USD_to_DEPOSIT_and_buy_BTC(class_info_in):
    res = class_info_in.USD_DEPO_BTC()

    print()
    print('USD на карте=', res['x'])
    print('USD перевелось на депозит(указать эту сумму):', res['x_depo'], 'с учетом остатка:', res['x_depo_sum'])
    print('BTC за все USD:', np.round(res['btc'],8),'  ')
    print('Остаток USD',res['x_resed'])
    print('------------------------------------------')
    return res


def info_USD_exc_RUB_to_DEPOSIT_and_buy_BTC(class_info_in):
    res = class_info_in.USD_DEPO_BTC_v2()
    print()
    print('USD на карте=', res['x'])
    print('RUB exchanged:', res['x_exch'])
    print('RUB перевелось на депозите(указать эту сумму):', res['x_depo'], 'с остатком :', res['x_depo_sum'])
    print('BTC за все RUB:', np.round(res['btc'],8))
    print('Остаток RUB',res['x_resed'])
    print('------------------------------------------')
    return res

def info_USD_to_DEPOSIT_buy_BTC_2var(class_info_in):
    r1 = info_USD_to_DEPOSIT_and_buy_BTC(class_info_in)
    r2 =info_USD_exc_RUB_to_DEPOSIT_and_buy_BTC(class_info_in)

    dBTC = np.round(r1['btc'],8)-np.round(r2['btc'],8)
    print('Разница BTC(usd-rub)', dBTC)
    print('Разница в RUB', dBTC*r2['price_r'])
    print('Разница в USD', dBTC * r1['price_u'])


#---------------
def info_RUB_to_DEPOSIT_and_buy_BTC(class_info_in):
    res = class_info_in.RUB_DEPO_BTC()

    print()
    print('RUB на карте=', res['x'])
    print('RUB перевелось на депозит(указать эту сумму):', res['x_depo'], 'с учетом остатка:', res['x_depo_sum'])
    print('BTC за все RUB:', np.round(res['btc'],8),'  ')
    print('Остаток RUB',res['x_resed'])
    print('------------------------------------------')
    return res


def info_RUB_exc_USD_to_DEPOSIT_and_buy_BTC(class_info_in):
    res = class_info_in.RUB_DEPO_BTC_v2()
    print()
    print('RUB на карте=', res['x'])
    print('USD exchanged:', res['x_exch'])
    print('USD перевелось на депозите(указать эту сумму):', res['x_depo'], 'с остатком :', res['x_depo_sum'])
    print('BTC за все USD:', np.round(res['btc'],8))
    print('Остаток USD',res['x_resed'])
    print('------------------------------------------')
    return res

def info_RUB_to_DEPOSIT_buy_BTC_2var(class_info_in):
    r1 = info_RUB_to_DEPOSIT_and_buy_BTC(class_info_in)
    r2 = info_RUB_exc_USD_to_DEPOSIT_and_buy_BTC(class_info_in)

    dBTC = np.round(r1['btc'],8)-np.round(r2['btc'],8)
    print('Разница BTC(usd-rub)', dBTC)
    print('Разница в USD', dBTC * r2['price_u'])
    print('Разница в RUB', dBTC * r1['price_r'])


if __name__ == '__main__':

    # Параметры

    taker = TradeConfig.TAKER

    api = ApiProvider().get()


    # Комиссии при транзакции
    mk_tk_usd = taker
    mk_tk_rub = taker

    # Курсы валют
    bank_sell_usd = 63.9
    bank_buy_usd = 63.25

    # Состояние депозита
    x_usd_depo = 0.00
    x_rub_depo = 0
    btc_depo = 0.00000000

    #Цена


    p_u_a = api.current_prices('BTC/USD')['bestAsk'] # При быстрой покупке, берем по цене, за которую  продают  комиссия taker
    p_r_a = api.current_prices('BTC/RUB')['bestAsk']  # При быстрой покупке, берем по цене, за которую  продают

    p_u_b = api.current_prices('BTC/USD')['bestBid']  # При быстрой покупке, берем по цене, за которую  продают  комиссия taker
    p_r_b = api.current_prices('BTC/RUB')['bestBid']  # При быстрой покупке, берем по цене, за которую  продают

    p_u=8270
    p_r=1

    #На карте
    x_usd=1
    x_rub=2000


    print('Цена для расчета:', p_u, 'usd', 'asks',p_u_a,'bids',p_u_b, 'delta:', p_u_a-p_u_b)
    print('Цена для расчета:', p_r, 'usd', 'asks', p_r_a, 'bids', p_r_b, 'delta:', p_r_a - p_r_b)


    #Класс для подсчета информаци
    cl_inToDep = InfoCalcToDep()
    cl_inToDep.setCurr(bank_buy_usd,bank_sell_usd)
    cl_inToDep.setUsdPrmt(price_tobuy_btcusd=p_u_a,maker_taker=mk_tk_usd,resedual_usd=0)          #Цену надо менять
    cl_inToDep.setRubPrmt(price_tobuy_btcrub=p_r_a, maker_taker=mk_tk_rub, resedual_rub=0)        #Цену надо менять
    cl_inToDep.setDepoBalance(resedual_usd=x_usd_depo,resedual_rub=x_rub_depo)
    cl_inToDep.setX(x_usd=x_usd,x_rub=x_rub) #На карте

    #Вывод информации
    #info_USD_to_DEPOSIT_and_buy_BTC(cl_inToDep)
    #info_USD_exc_RUB_to_DEPOSIT_and_buy_BTC(cl_inToDep)  #второй вариант ввода
    #info_USD_to_DEPOSIT_buy_BTC_2var(cl_inToDep)        #Два варианта

    #info_RUB_to_DEPOSIT_and_buy_BTC(cl_inToDep)
    #info_RUB_exc_USD_to_DEPOSIT_and_buy_BTC(cl_inToDep)
    info_RUB_to_DEPOSIT_buy_BTC_2var(cl_inToDep)

    #Цена на обратный вывод