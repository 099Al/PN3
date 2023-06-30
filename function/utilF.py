# -*- coding: utf-8 -*-

import api.data as cexdata

#Последняя цена
def last_prices(base='BTC',quote='USD',delta_price=0):
    '''
    :param delta_price: Изменение цены, чтобы mk_taker был не равен taker
    :return:
    '''

    price_btc = float(cexdata.lastprice(base,quote)['lprice'])

    price_btc = price_btc + delta_price  #либо параметр прописывается напрямую

    return price_btc

def current_price(base='BTC',quote='USD'):
    ord = cexdata.orderbook(base, quote)

    price_bids = ord['bids'][0][0]   #buy order
    price_asks = ord['asks'][0][0]   #sell order

    return {'bids':price_bids,'asks':price_asks}


if  __name__ == '__main__':

    print(current_price(base='BTC',quote='USD')['bids'])
    print(current_price(base='BTC',quote='USD')['asks'])