# -*- coding: utf-8 -*-


'''Функции для расчета вывода крипты в RUB и USD'''


from function.transacFunction import sellBTC
from deposit.function.depoMoneyInOut import X_WITHD

# Вывод BTC
def BTC_WITHDR(btc,price_btc,mk_tk,comiss_out_pr,commis_out_f):
    # mk_tk - коммиссия при транзакции
    # comiss_out_pr - комиссия при выводе процент
    # commis_out_f - комиссия при выводе фиксированная

    #pre sell не использууется, т.к. результат r будет тем же
    #т.к. идет просто расчет, с баланса btc не списывается
    r = sellBTC(btc,price_btc,mk_tk)
    X = r['x']  # сумма на балансе

    #вывод с баланса
    xOut = X_WITHD(X,comiss_out_pr,commis_out_f)

    return xOut



# Вывод BTC в RUB
# Используется среднее значение maker_taker
def BTC_OUT_RUB(btc,price_btcrub,mk_tk_comiss=-1):
    from deposit.feeslimits.constant import mk_tk
    from deposit.feeslimits.constant import com_pr_r,com_f_r #комисси при выводе в рублях

    if(mk_tk_comiss==-1):      #если значение не выставилось, то присваивается дефолтное
        mk_tk_comiss = mk_tk

    x_r  = BTC_WITHDR(btc,price_btcrub,mk_tk_comiss,com_pr_r,com_f_r)

    return x_r



# Вывод в USD
# Используется среднее значение maker_taker
def BTC_OUT_USD(btc,price_btcusd,mk_tk_comiss=-1):
    from deposit.feeslimits.constant import mk_tk
    from deposit.feeslimits.constant import com_pr_u, com_f_u  # комисси при выводе в USD

    if (mk_tk_comiss == -1):  # если значение не выставллось, то присваивается дефолтное
        mk_tk_comiss = mk_tk

    x_r  = BTC_WITHDR(btc,price_btcusd,mk_tk_comiss,com_pr_u,com_f_u)

    return x_r
