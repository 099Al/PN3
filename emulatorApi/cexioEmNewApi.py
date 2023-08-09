# -*- coding: utf-8 -*-

import hmac
import hashlib
import time
import requests
import json
import base64
from datetime import datetime


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
    def __init__(self,username,unix_curr_time,api_key=None, api_secret=None):
        self.username = username
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

        """ко времени self.unix_curr_time добавляется несколько секунд.
        Т.к. на самом деле, время транзакции происходит с задержкой"""

        pairs = market.split('/')
        p1 = pairs[0]
        p2 = pairs[1]

        #CHECK BALANCE
        from db.connection import DBConnect
        conn = DBConnect().getConnect()
        cursor = conn.cursor()
        res = cursor.execute('SELECT AMOUNT FROM IM_BALANCE WHERE CURR = ?',(p2,))
        balance_sum = res.fetchone()[0]


        need_amt=price*amount #+fee need to calc

        transactTime = datetime.utcfromtimestamp((self.unix_curr_time + 2000) / 1000).strftime('%Y-%m-%dT%H:%M:%S.') + f'{(self.unix_curr_time + 2000) % 1000:03d}Z'
        #unix_dt = int(datetime.now().timestamp() * 1000)  #выводит по времени UTC+0

        from perfomance.cache.values import ValuesOrder
        ValuesOrder.orderId = ValuesOrder.orderId + 1


        if balance_sum>=need_amt:


            res = {'ok': 'ok', 'data': {'messageType': 'executionReport'
                                        , 'clientId': self.username
                                        , 'orderId': ValuesOrder.orderId
                                        , 'clientOrderId': self.unix_curr_time
                                        , 'accountId': ''
                                        , 'status': 'NEW'
                                        , 'currency1': pairs[0]
                                        , 'currency2': pairs[1]
                                        , 'side': 'BUY'
                                        , 'executedAmountCcy1': '0.00000000'
                                        , 'executedAmountCcy2': '0.00000000'
                                        , 'requestedAmountCcy1': amount
                                        , 'requestedAmountCcy2': None
                                        , 'orderType': 'Limit'
                                        , 'timeInForce': 'GTC'
                                        , 'comment': None
                                        , 'executionType': 'New'
                                        , 'executionId':  f'{str(self.unix_curr_time)}_X_{ValuesOrder.orderId}'  #Просто число. Логика формирования не понятно. Но и не нужна
                                        , 'transactTime': transactTime
                                        , 'expireTime': None
                                        , 'effectiveTime': None
                                        , 'price': price
                                        , 'averagePrice': None
                                        , 'feeAmount': '0.00000000'
                                        , 'feeCurrency': pairs[1]   #USD
                                        , 'clientCreateTimestamp':  self.unix_curr_time
                                        , 'serverCreateTimestamp': self.unix_curr_time+1000
                                        , 'lastUpdateTimestamp':    self.unix_curr_time+10000}}

            #change balance
            new_balance = balance_sum - need_amt

            cursor.execute('UPDATE IM_BALANCE SET AMOUNT = ?, RESERVED = ? WHERE CURR = ?', (new_balance,need_amt,p2))



            conn.comit()


        else:
            res = {'ok': 'ok', 'data': {'messageType': 'executionReport'
                                        , 'clientId': self.username
                                        , 'orderId': ValuesOrder.orderId
                                        , 'clientOrderId': self.unix_curr_time
                                        , 'accountId': ''
                                        , 'status': 'REJECTED'
                                        , 'currency1': pairs[0]
                                        , 'currency2': pairs[1]
                                        , 'side': 'BUY'
                                        , 'executedAmountCcy1': '0.00000000'
                                        , 'executedAmountCcy2': '0.00000000'
                                        , 'requestedAmountCcy1': amount
                                        , 'requestedAmountCcy2': None
                                        , 'orderType': 'Limit'
                                        , 'timeInForce': 'GTC'
                                        , 'comment': None
                                        , 'executionType': 'Rejected'
                                        , 'executionId': f'{str(self.unix_curr_time)}_X_{ValuesOrder.orderId}'
                                        , 'transactTime': transactTime
                                        , 'expireTime': None
                                        , 'effectiveTime': None
                                        , 'price': '30100.0'
                                        , 'averagePrice': None
                                        , 'feeAmount': None
                                        , 'feeCurrency': None
                                        , 'orderRejectReason': '{"code":403,"reason":"Insufficient funds"}'
                                        , 'rejectCode': 403
                                        , 'rejectReason': 'Insufficient funds'
                                        , 'clientCreateTimestamp': self.unix_curr_time
                                        , 'serverCreateTimestamp': self.unix_curr_time + 1000
                                        , 'lastUpdateTimestamp': self.unix_curr_time + 10000}}


        return res

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



    api = emulatorApi('test_user',1689533488861)
    api.buy_limit_order(0.005,30000)

    #dt = datetime.fromtimestamp(1689533488)
    dt = datetime.utcfromtimestamp(1689533488860/1000).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    dt2 = datetime.utcfromtimestamp(1689533488860 / 1000).strftime('%Y-%m-%dT%H:%M:%S.')+f'{1689533488860 % 1000:03d}Z'

    formatted_datetime_with_milliseconds = dt[:-1] + f"{1689533488860 % 1000:03d}Z"
    print(dt)
    print(dt2)