# -*- coding: utf-8 -*-

"""
    See https://cex.io/rest-api
    copy cexio __init__ file from cexio package
"""
import hmac
import hashlib
import time
import requests

BASE_URL = 'https://cex.io/api/%s/'

PUBLIC_COMMANDS = {
    'currency_limits',
    'ticker',
    'last_price',
    #'last_prices',
    'convert',
    #'price_stats',
    'order_book',
    'trade_history'
}


class Api:
    """
    Python wrapper for CEX.IO
    """

    def __init__(self, username, api_key, api_secret):
        self.username = username
        self.api_key = api_key
        self.api_secret = api_secret

    @property
    def __nonce(self):
        """Всегда должна увеличиваться. Время оптимальный вариант"""
        return str(int(time.time() * 1000))

    def __signature(self, nonce):
        """зависит от nonce, который всегда меняется, следовательно signature всегда должна меняться
           зависит от api_key и secret_key
        """

        message = nonce + self.username + self.api_key
        signature = hmac.new(bytearray(self.api_secret.encode('utf-8')), message.encode('utf-8'),
                             digestmod=hashlib.sha256).hexdigest().upper()
        return signature

    def api_call(self, command, param=None, market=''):
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

        if command not in PUBLIC_COMMANDS:
            nonce = self.__nonce
            param.update({
                'key': self.api_key,
                'signature': self.__signature(nonce),
                'nonce': nonce
            })

        request_url = (BASE_URL % command) + market

        result = self.__post(request_url, param)

        return result

    def __post(self, url, param):

        result = requests.post(url, data=param, headers={'User-agent': 'bot-' + self.username}).json()
        return result


    #PUBLIC COMMANDS
    @property
    def currency_limits(self):
        return self.api_call('currency_limits')
    def ticker(self, market='BTC/USD'):
        return self.api_call('ticker', None, market)

    def last_price(self, market='BTC/USD'):
        return self.api_call('last_price', None, market)

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

    def trade_history(self,market):
        return self.api_call('trade_history', None, market)





    #PRIVATE COMMANDS
    #@property
    def balance(self):
        return self.api_call('balance')

    def get_myfee(self):
        return self.api_call('get_myfee')

    def open_orders(self, market):
        return self.api_call('open_orders', None, market)

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

    """
    example
    result = requests.post('https://cex.io/api/convert', data={'amnt': 1}, headers={'User-agent': 'bot-' + self.username}).json()
    
    result = requests.post('https://cex.io/api/balance/', data={'key': 'api_key'
                                       , 'signature': '3477A04...'
                                       , 'nonce': '1689185788390'}
                              , headers={'User-agent': 'bot-' + self.username}).json()
    
    """

    from configs import config

    api = Api(config.API_USER, config.API_KEY, config.API_SECRET)

    #test public
    #last_price = api.last_price()

    #test private
    balance = api.balance()

    #last_price = api.convert(1)


    print(result)

