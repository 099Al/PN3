from api.cexioNewApi import Api
from configs import config
from manualTraiding.preCalcTrans.info_trade import info_parameters_to_buy_BTC,info_parameters_to_sell_BTC,info_expected_price_sellBTC

if __name__ == '__main__':

    api = Api(config.API_USER, config.API_KEY, config.API_SECRET)


    #bestAsk - продать по  bestBid - купить по
    prices = api.current_prices('BTC/USD')
    print(prices)

    #exit()

    price = 25700
    x = 15
    info_parameters_to_buy_BTC(price, x)
    print('------')

    # buy_req = api.buy_limit_order(0.00058257, 25700)
    # print(buy_req)

    #{'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '235818', 'clientOrderId': '1694186578288', 'accountId': '', 'status': 'NEW', 'currency1': 'BTC', 'currency2': 'USD',
    #{'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '235820', 'clientOrderId': '1694186805729'


    #cancel_all = api.cancel_all_order() #{'ok': 'ok', 'data': {'clientOrderIds': ['1694186578288']}}
    #print(cancel_all)

    #cancel_order = api.cancel_order(235820)
    #print('cancel_order',cancel_order)

    # cancel_order = api.cancel_client_order(1694187928008)
    # print('cancel_order',cancel_order)

    orders = api.open_orders()
    print('orders', orders)

    transaction_history = api.transaction_history()
    print(transaction_history)

    exit()

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




