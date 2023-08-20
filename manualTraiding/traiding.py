from PN3.configs.feeslimits.constant import mk_tk,taker
from PN3.function.utilF import last_prices,current_price

# Комиссии при транзакции
mk_tk_usd = mk_tk
mk_tk_rub = mk_tk



if __name__ == '__main__':

    # Параметры



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