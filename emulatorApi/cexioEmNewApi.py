# -*- coding: utf-8 -*-

import hmac
import hashlib
import time
import requests
import json
import base64


from db.connection import DBConnect


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

class emulatorApi:
    """
    Python wrapper for CEX.IO
    """
    #conn=None
    #curr_time=0
    def __init__(self,unix_curr_time):
        self.unix_curr_time=unix_curr_time
        dbconn = DBConnect()
        self.conn = dbconn.getConnect()

    def close(self):
        conn.close()


    def api_call(self,param1,param2):
        pass


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

        cur = self.conn.cursor()
        sel_res = cur.execute(f"SELECT trade_data FROM im_cex_history_tik where unixdate<= {self.unix_curr_time} order by unixdate desc limit 1000");

        res = {'ok': 'ok', 'data': {'pageSize': 1000, 'trades': [ json.loads(x[0]) for x in sel_res.fetchall()] }}


        return res



    def ticker(self,pairs=['BTC/USD']):
        pairs = list(map(lambda x:x.replace('/','-'),pairs))
        param = {'pairs':pairs}
        return self.api_call('get_ticker', param)

    # PRIVATE COMMANDS

    def account_status(self):
        param = {"accountIds": []}
        return self.api_call('get_my_account_status_v2',param)

    def get_myfee(self):
        return self.api_call('get_myfee')

    def open_orders(self, params=None):
        return self.api_call('get_my_orders', params)

    def order_book(self, params={'pair':'BTC-USD'}):
        return self.api_call('get_order_book',params)

    def get_order(self, order_id):
        return self.api_call('get_order', {'id': order_id})

    def set_order(self, amount, price, sell_buy, orderType='Limit',market='BTC/USD',clientOrderId=None):

        #GTC - выход пока н еисполнится
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

    def sell_limit_order(self, amount, price, market='BTC/USD',clientOrderId=None):

        pairs = market.split('/')
        unix_dt = int(datetime.now().timestamp())  #выводит по времени UTC+0

        params = {
            "currency1": pairs[0]
            ,"currency2": pairs[1]
            ,"side": "SELL"
            ,"timestamp": unix_dt
            ,"orderType": "Limit"
            ,"timeInForce": "GTC"
            ,"amountCcy1": amount
            ,"price": price
            #"comment": "v_overdraft_test"
        }

        if clientOrderId is not None:
            params.update({"clientOrderId":clientOrderId})

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

    def cancel_order(self, clientOrderId):

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


if __name__ == '__main__':
    from datetime import datetime

    from configs import config



    api = Api()

