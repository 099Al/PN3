# -*- coding: utf-8 -*-

import hmac
import hashlib
import time
import requests
import json
import base64
from datetime import datetime

from src.api.base_api import BaseApi
from src.config import prj_configs

BASE_PUBLIC_URL = 'https://trade.cex.io/api/spot/rest-public/%s'  #do not use / at the end
BASE_PRIVATE_URL = 'https://trade.cex.io/api/spot/rest/%s'

PUBLIC_COMMANDS = {
     'get_order_book'
    ,'get_candles'
    ,'get_trade_history'
    ,'get_ticker'
    ,'get_server_time'
    ,'get_pairs_info'
    ,'get_currencies_info'
    ,'get_processing_info'
}

VALID_RESOLUTIONS = {"1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d"}
VALID_DATATYPE = {"bestAsk", "bestBid"}

class Api(BaseApi):
    """
    Python wrapper for CEX.IO
    """

    def __init__(self, username, api_key, api_secret):
        self.username = username
        self.api_key = api_key
        self.api_secret = api_secret


    def __nonce(self,tmstamp=None):
        """Всегда должна увеличиваться. Время оптимальный вариант"""
        if tmstamp is None:
            tm = time.time()
        else:
            tm=tmstamp
        return str(int(tm * 1000))

    def __signature(self, nonce, action, param):
        """зависит от nonce, который всегда меняется, следовательно signature всегда должна меняться
           зависит от api_key и secret_key
        """
        message = action+str(nonce)+json.dumps(param)
        #signature = hmac.new(bytearray(self.api_secret.encode('utf-8')),digestmod=hashlib.sha256).update(message.encode('utf-8'))
        signature = hmac.new(bytearray(self.api_secret.encode('utf-8')), message.encode('utf-8'), digestmod=hashlib.sha256)
        signature = signature.digest()
        signature = base64.b64encode((signature)).decode('utf-8')

        return signature

    def api_call(self, command, param=None):
        """
        Если команда не public, тогда параметры передаются как есть
        Если private, то добавляются key, signature в params

        :param command: Query command for getting info   example:trade_history
        :type commmand: str

        :param param: Extra options for query  example: {}
        :type options: dict

        :return: JSON response from CEX.IO
        :rtype : dict
        """

        if param is None:
            param = {}

        if command in PUBLIC_COMMANDS:
            headers = {
                'Content-type': 'application/json',
                'User-Agent': 'client'
            }
            request_url = (BASE_PUBLIC_URL % command)

        else:

            now_stamp = int(time.time())
            signature = self.__signature(now_stamp, command, param)
            headers = {
                'X-AGGR-KEY': self.api_key,
                'X-AGGR-TIMESTAMP': str(now_stamp),
                'X-AGGR-SIGNATURE': signature,
                'Content-Type': 'application/json'
                #'User-Agent': 'client'
            }

            request_url = (BASE_PRIVATE_URL % command)

        result = self.__post(request_url, param, headers)

        return result

    def __post(self, url, param, headers):
        #print(url)
        #print(param)
        #print(headers)
        result = requests.post(url, json=param, headers=headers)
        return result.json()


    # PUBLIC COMMANDS
    def currencies_info(self):
        return self.api_call('get_currencies_info')


    def candles(self,dataType,pair='BTC-USD',limit=None,resolution='1h',fromDT=None,toDT=None):

        if dataType:
            if dataType not in VALID_DATATYPE:
                return {'Bad _data Type'}

        if resolution:
            if resolution not in VALID_RESOLUTIONS:
                return {'Not valid resolution'}

        param = {
            "pair": pair,
            "fromISO": fromDT,
            "toISO": toDT,
           # "limit": limit,
            "dataType": dataType,
            "resolution": resolution
        }

        return self.api_call('get_candles',param)

    def trade_history(self,pair='BTC-USD'):

        pair = pair.replace(',','-')

        param = {'pair':pair}
        return self.api_call('get_trade_history', param)



    def ticker(self,pairs=['BTC/USD']):
        pairs = list(map(lambda x: x.replace('/','-'),pairs))
        param = {'pairs': pairs}
        return self.api_call('get_ticker', param)




    # PRIVATE COMMANDS

    def account_status(self):
        param = {"accountIds": []}
        return self.api_call('get_my_account_status_v2',param)

    def get_myfee(self):
        return self.api_call('get_my_fee')

    #завершенные сделки
    def transaction_history(self):
        return self.api_call('get_my_transaction_history')

    def open_orders(self, params=None):
        return self.api_call('get_my_orders', params)

    def get_order(self,order_id):
        return self.api_call('get_my_orders', {'id': order_id})



    #стакан
    def order_book(self, params={'pair':'BTC-USD'}):
        return self.api_call('get_order_book', params)



    def set_order(self, amount, price, sell_buy, orderType='Limit',market='BTC/USD',clientOrderId=None):

        #GTC - выход пока не исполнится
        #GTD- выход по истечении времени

        pairs = market.split('/')
        unix_dt = int(datetime.now().timestamp())  # выводит по времени UTC+0

        params = {
              "currency1": pairs[0]
            , "currency2": pairs[1]
            , "side": sell_buy
            , "timestamp": unix_dt
            , "orderType": orderType  #Limit Market
            , "timeInForce": "GTC"
            , "amountCcy1": amount
            , "price": price
            # "comment": "v_overdraft_test"
        }

        if clientOrderId is not None:
            params.update({"clientOrderId": clientOrderId})

        return self.api_call('do_my_new_order', params)

    def sell_limit_order(self, amount, price,clientOrderId=None,market='BTC/USD'):

        pairs = market.split('/')
        unix_dt = int(datetime.now().timestamp() * 1000)  #выводит по времени UTC+0

        params = {
            "clientOrderId": f'{unix_dt}'
            ,"currency1": pairs[0]
            ,"currency2": pairs[1]
            ,"side": "SELL"
            ,"timestamp": unix_dt
            ,"orderType": "Limit"
            ,"timeInForce": "GTC"
            ,"amountCcy1": amount
            ,"price": price
            #"comment": "v_overdraft_test"
        }

        #if clientOrderId is not None:
        #    params.update({"clientOrderId":clientOrderId})

        return self.api_call('do_my_new_order',params)

    def buy_limit_order(self, amount, price, clientOrderId=None, market='BTC/USD'):

        pairs = market.split('/')
        unix_dt = int(datetime.now().timestamp() * 1000)  #выводит по времени UTC+0

        params = {
            "clientOrderId": f'{unix_dt}'
            ,"currency1": pairs[0]
            ,"currency2": pairs[1]
            ,"side": "BUY"
            ,"timestamp": unix_dt
            ,"orderType": "Limit"
            ,"timeInForce": "GTC"
            ,"amountCcy1": amount
            ,"price": price
            #"comment": "v_overdraft_test"
        }

        #if clientOrderId is not None:
        #    params.update({"clientOrderId":clientOrderId})

        return self.api_call('do_my_new_order',params)

    def cancel_order(self, OrderId):

        unix_dt = int(datetime.now().timestamp()*1000)
        param = {
            "orderId": OrderId,
            #"clientOrderId": f'{clientOrderId}',
            "cancelRequestId": f"cancel_{OrderId}",
            "timestamp": unix_dt
        }

        return self.api_call('do_cancel_my_order',param)

    def cancel_client_order(self, clientOrderId):

        unix_dt = int(datetime.now().timestamp()*1000)
        param = {
            "clientOrderId": f'{clientOrderId}',
            "cancelRequestId": f"cancel_{clientOrderId}",
            "timestamp": unix_dt
        }

        return self.api_call('do_cancel_my_order',param)

    def cancel_all_order(self):
        param = {}
        return self.api_call('do_cancel_all_orders',param)


    #CUSTOM COMMANDS
    def limit_info(self,pairs = 'BTC/USD'):
        pairs = pairs.replace('/', '-')
        base, quote = pairs.split('-')
        data = self.api_call('get_pairs_info')['data']
        info = list(filter(lambda x: x['base'] == base and x['quote'] == quote, data))[0]
        return info


    def current_prices(self,pair = 'BTC/USD'):
        pairs = pair.replace('/', '-')
        res = self.ticker(pairs=[pairs])['data'][pairs]
        bestBid = res['bestBid']
        bestAsk = res['bestAsk']
        return {'bestBid': bestBid, 'bestAsk': bestAsk}

    def fee(self, pair='BTC/USD'):
        pair = pair.replace('/', '-')
        res = self.api_call('get_my_fee')
        fee = res['data']['tradingFee'][pair]['percent']
        return fee


