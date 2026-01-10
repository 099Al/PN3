# -*- coding: utf-8 -*-

import numpy as np

from src.trade_parameters import TradeConfig
from src.trade_utils.trade import sellBTC

MAKER_TAKER = TradeConfig.MAKER_TAKER

# комисси при выводе в USD
com_pr_r = TradeConfig.r_dep_prc
com_f_r = TradeConfig.r_dep_fix

#комисси при выводе в рублях
com_pr_u = TradeConfig.u_wthrw_prc
com_f_u = TradeConfig.u_wthrw_fix


#Ввод на депозит

#x - сумма, которая тратится (с карты)
def X_to_DEPO(x, percent, fix):
    comis = x*percent/100+fix  # процент берется от того, что тратится
    x_dep = round(x-comis, 2)  # сумма, которая будет на депозите
    # print('xd=',comis)
    return x_dep          # Будет на депозите.   Проверена

#Вывод
def X_WITHD(x, percent, fix):
    comis = x * percent / 100 + fix
    return np.round(x - comis, 2)


#Необходимо на депозите, чтобы вывести X
def Xdepo_for_Xout(Xout, percent, fix):
    depoX = (Xout+fix)/(1-percent/100)
    return depoX



# Вывод BTC
def _BTC_WITHDR(btc, price_btc, mk_tk, comiss_out_pr, commis_out_f):
    # mk_tk - коммиссия при транзакции
    # comiss_out_pr - комиссия при выводе процент
    # commis_out_f - комиссия при выводе фиксированная

    #pre sell не использууется, т.к. результат r будет тем же
    #т.к. идет просто расчет, с баланса btc не списывается
    r = sellBTC(btc, price_btc, mk_tk)
    X = r['x']  # сумма на балансе

    #вывод с баланса
    xOut = X_WITHD(X, comiss_out_pr, commis_out_f)

    return xOut



# Вывод BTC в RUB
# Используется среднее значение maker_taker
def BTC_OUT_RUB(btc,price_btcrub,mk_tk_comiss=-1):

    if(mk_tk_comiss==-1):      #если значение не выставилось, то присваивается дефолтное
        mk_tk_comiss = MAKER_TAKER

    x_r  = _BTC_WITHDR(btc, price_btcrub, mk_tk_comiss, com_pr_r, com_f_r)

    return x_r



# Вывод в USD
# Используется среднее значение maker_taker
def BTC_OUT_USD(btc, price_btcusd, mk_tk_comiss=-1):

    if (mk_tk_comiss == -1):  # если значение не выставллось, то присваивается дефолтное
        mk_tk_comiss = MAKER_TAKER

    x_r = _BTC_WITHDR(btc, price_btcusd, mk_tk_comiss, com_pr_u, com_f_u)

    return x_r


if __name__ == '__main__':

    #r = X_to_DEPO(75.19, 2.99, 0)
    r = Xdepo_for_Xout(1000, 3, 50)
    print(r)