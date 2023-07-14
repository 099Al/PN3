# -*- coding: utf-8 -*-

import hmac
import hashlib
import time
import requests
import json
import base64

BASE_PUBLIC_URL = 'https://api.plus.cex.io/rest-public/%s'  #do not use / at the end
BASE_PRIVATE_URL = 'https://api.plus.cex.io/rest/%s'

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

class Api:
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

    def __signature(self, nonce,action,param):
        """зависит от nonce, который всегда меняется, следовательно signature всегда должна меняться
           зависит от api_key и secret_key
        """
        message = action+str(nonce)+json.dumps(param)
        #signature = hmac.new(bytearray(self.api_secret.encode('utf-8')),digestmod=hashlib.sha256).update(message.encode('utf-8'))
        signature = hmac.new(bytearray(self.api_secret.encode('utf-8')), message.encode('utf-8'), digestmod=hashlib.sha256)
        signature = signature.digest()
        signature = base64.b64encode((signature)).decode('utf-8')
        print('s',signature)
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
            print(now_stamp,type(now_stamp))
            signature = self.__signature(now_stamp,command,param)
            headers = {
                'X-AGGR-KEY': self.api_key,
                'X-AGGR-TIMESTAMP': str(now_stamp),
                'X-AGGR-SIGNATURE': signature,
                'Content-Type': 'application/json'
                #'User-Agent': 'client'
            }
            print('nonce',now_stamp)
            print('command',command)
            print('param',param)
            print(signature)
            request_url = (BASE_PRIVATE_URL % command)
            print(request_url)
        result = self.__post(request_url,param,headers)

        return result

    def __post(self, url, param, headers):
        #print(url)
        #print(param)
        #print(headers)
        result = requests.post(url, json=param, headers=headers)
        print('res',result)
        return result.json()


    # PUBLIC COMMANDS
    def currencies_info(self):
        return self.api_call('get_currencies_info')

    def candles(self,dataType,pair='BTC-USD',limit=None,resolution='1h',fromDT=None,toDT=None):

        if dataType:
            if dataType not in VALID_DATATYPE:
                return {'Bad data Type'}

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







    def convert(self, amount=1, market='BTC/USD'):
        """
        Converts any amount of the currency to any other currency by multiplying the amount
        by the last price of the chosen pair according to the current exchange rate.

        :param amount: Convertible amount
        :type amount: float

        :return: Amount in the target currency
        :rtype: dict
        """
        return self.api_call('convert', {'amnt': amount}, market)

    def order_book(self, depth=1, market='BTC/USD'):
        return self.api_call('order_book', None, market + '/?depth=' + str(depth))



    # PRIVATE COMMANDS
    # @property
    def account_status(self):
        param = {"accountIds": []}
        return self.api_call('get_my_account_status_v2',param)

    def get_myfee(self):
        return self.api_call('get_myfee')

    def open_orders(self, params=None):
        return self.api_call('get_my_orders', params)

    def cancel_order(self, order_id):
        return self.api_call('cancel_order', {'id': order_id})

    def buy_limit_order(self, amount, price, market):
        params = {
            'type': 'buy',
            'amount': amount,
            'price': price
        }

        return self.api_call('place_order', params, market)

    def sell_limit_order(self, amount, price, market):
        params = {
            'type': 'sell',
            'amount': amount,
            'price': price
        }

        return self.api_call('place_order', params, market)

    def open_long_position(self, amount, symbol, estimated_open_price, stop_loss_price, leverage=2, market='BTC/USD'):
        params = {
            'amount': amount,
            'symbol': symbol,
            'leverage': leverage,
            'ptype': 'long',
            'anySlippage': 'true',
            'eoprice': estimated_open_price,
            'stopLossPrice': stop_loss_price
        }

        return self.api_call('open_position', params, market)

    def open_short_position(self, amount, symbol, estimated_open_price, stop_loss_price, leverage=2, market='BTC/USD'):
        params = {
            'amount': amount,
            'symbol': symbol,
            'leverage': leverage,
            'ptype': 'short',
            'anySlippage': 'true',
            'eoprice': estimated_open_price,
            'stopLossPrice': stop_loss_price
        }

        return self.api_call('open_position', params, market)

    def open_positions(self, market='BTC/USD'):
        return self.api_call('open_positions', None, market)

    def close_position(self, position_id, market='BTC/USD'):
        return self.api_call('close_position', {'id': position_id}, market)

    def get_order(self, order_id):
        return self.api_call('get_order', {'id': order_id})


if __name__ == '__main__':
    from datetime import datetime

    from configs import config



    api = Api(config.API_USER, config.API_KEY, config.API_SECRET)

    # test public
    #currencies_info = api.currencies_info()

    #fromDT = int(datetime.now().timestamp())-3600*2
    #toDT = int(datetime.now().timestamp()) - 5
    #currencies_info = api.candles(dataType='bestAsk',fromDT=fromDT,toDT=toDT)
    #print(currencies_info)

    #trade_hist = api.trade_history()
    #print(trade_hist)

    # test private
    #balance = api.balance()
    status = api.account_status()

    #status = api.open_orders()
    print(status)



