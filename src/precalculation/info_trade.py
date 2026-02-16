# -*- coding: utf-8 -*-

import src.trade_utils.trade as trade
import src.precalculation.deltas as delta


# Основные функции----------
# Параметры для установки ордера на покупку
# Какое кол-во btc и по какой цене, чтобы взять на X(на всю сумму)
def info_parameters_to_buy_BTC(price, x):
    step = 10
    btc_n = trade.buyBTC(x, price)
    print("BTC_max_0=", btc_n, "price=", price)

    print("max")
    for i in range(-5, 6):
        dp = i * step
        price_n = price + dp
        btc_n = trade.buyBTC(x, price_n)

        x1_n = trade.X_for_buyBTC(btc_n, price_n)

        if i == 0:
            print("---btc max=", btc_n, "price=", price_n, "x=", x1_n)
        else:
            print("btc max=", btc_n, "price=", price_n, "x=", x1_n)
    print("min")


# Параметры для установки ордера на продажу
def info_parameters_to_sell_BTC(btc, price, mk_tk, taker):

    step = 10

    print(f"Продать btc:{btc} по цене:{price}")
    btc_pre_n = trade.presellBTC(btc, price)
    x_n = trade.sellBTC(btc_pre_n, price, mk_tk)["x"]
    print(f"sell btc:{btc_pre_n} price:{price} result: {x_n} comiss mt:{mk_tk}%")
    for i in range(-5, 6):
        dp = i * step
        price_n = price + dp
        btc_pre_n = trade.presellBTC(btc, price_n)
        x_n = trade.sellBTC(btc_pre_n, price_n, mk_tk)["x"]
        x_n_taker = trade.sellBTC(btc_pre_n, price_n, taker)["x"]

        if i == 0:
            print(
                f"----sell btc:{btc_pre_n} price:{price_n} result: {x_n} - {x_n_taker} comiss_%: {mk_tk} - {taker}"
            )
        else:
            print(
                f"sell btc:{btc_pre_n} price:{price_n} result: {x_n} - {x_n_taker} comiss_%: {mk_tk} - {taker}"
            )


# -------------------------


# Изменение BTC при продаже по текущей цене и покупке по новой
def info_delta_BTC(btc, price_to_sell, price_exp_to_buy, buy_fee, sell_fee):

    dBTC = delta.deltaBTC(btc, price_to_sell, price_exp_to_buy, buy_fee)
    dBTC1 = delta.deltaBTC(btc, price_to_sell, price_exp_to_buy, sell_fee)

    print(
        "BTC0=", btc, "текущая цена=", price_to_sell, "ожидаемая цена", price_exp_to_buy
    )
    print("dBTC=", dBTC, "comiss=", buy_fee)
    print("dBTC=", dBTC1, "comiss=", sell_fee)


def info_delta_X(x0, price_to_buy, price_exp_to_sell, sell_fee):

    dx = delta.deltaX(x0, price_to_buy, price_exp_to_sell, sell_fee)["dx"]
    print()
    print("x0=", x0, "Цена при покупке BTC на x0=", price_to_buy)
    print("Цена при продаже=", price_exp_to_sell)
    print("изменения dx:", dx)
    print("итого:", x0 + dx)


# Продать сейчас BTC и найти цену, по которой можно получить btc_exp
def infoExpPrice_sellBTC0_buyBTC(btc0, current_price, btc_expected, commis):

    r = delta.priceForExpectBTC(btc0, current_price, btc_expected, commis)

    print("Продать btc0:", btc0, "По цене:", current_price)
    print("Получим X:", r["x"])
    print("Купиить X по ИСКОМОЙ цене:", r["price"])
    print("Получим:", btc_expected)


# Купить BTC  на X. Найти цену, по которой продать BTC для X
def info_expected_price_buyBTC_sellBTC(x0, current_price, x_expected, commis):

    r = delta.priceForExpectX(x0, current_price, x_expected, commis)

    print("Есть X=", x0, "купить на них btc=", r["maxbtc"], "по цене", r["price"])
    print("Продать btc_presell", r["sellbtc"], "получим X", x_expected)
    print("Искомая цена продажи", r["price"])


# Поиск цены для покупки BTC0
def infoExpPrice_buyBTC(X, btc_exp):

    p = trade.price_for_buy_btc(btc_exp, X)

    print("Для покупки BTC:", btc_exp, "На все X", X)
    print("Цена должна снизиться до", p)


def info_expected_price_sellBTC(x_exp, btc, sell_commis):

    # продажа имеющихся btc
    p_exp = trade.price_for_sell_btc(x_exp, btc, sell_commis)

    print(
        f'Для получения X:{x_exp} за BTC={btc} Цена продажи:{p_exp["price"]}  BTCpresell:{p_exp["btc"]}'
    )


# Остальные функции высчитывать на Практике


if __name__ == "__main__":

    # print("---BUY---")
    price = 66800
    x = 13
    info_parameters_to_buy_BTC(price, x)
    # print("----SELL----")
    # mk_tk = 0.25
    # taker = 0.16
    # info_parameters_to_sell_BTC(0.00019, price, mk_tk, taker)
    #
    # print("----PRICE------")
    # x_exp = 15
    # btc = 0.00057328
    # sell_commis = 0.25
    # info_expected_price_sellBTC(x_exp, btc, sell_commis)
