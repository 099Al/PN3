# -*- coding: utf-8 -*-

import json

from src.api.base_api import BaseApi
from trade_data.db.connection import DBConnect

from functions.trade import X_for_buyBTC
from configs.config import BASE_MIN
from trade_data.queriesDB import balance_state

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

class EmulatorApi(BaseApi):
    """
    Python wrapper for CEX.IO
    """
    #conn=None
    #curr_time=0
    def __init__(self,username,unix_curr_time,api_key=None, api_secret=None):
        self.username = username
        self.unix_curr_time = unix_curr_time
        dbconn = DBConnect()
        self.conn = dbconn.getConnect()

    def __nonce(self,tmstamp=None):
        pass



    def close(self):
        self.conn.close()


    def api_call(self, command, param = None):
        pass


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

        cur = self.conn.cursor()
        sel_res = cur.execute(f"SELECT trade_data FROM im_cex_history_tik where unixdate<= {self.unix_curr_time} order by unixdate desc limit 1000");

        res = {'ok': 'ok', 'data': {'pageSize': 1000, 'trades': [ json.loads(x[0]) for x in sel_res.fetchall()] }}


        return res



    def ticker(self, pairs=['BTC/USD']):
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

        # orders {'ok': 'ok', 'data': [{'orderId': '189237', 'clientOrderId': '72379967642F', 'clientId': 'up112344963', 'accountId': None, 'status': 'NEW', 'statusIsFinal': False, 'currency1': 'BTC', 'currency2': 'USD', 'side': 'SELL', 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'rejectCode': None, 'rejectReason': None, 'initialOnHoldAmountCcy1': '0.00057328', 'initialOnHoldAmountCcy2': None, 'executedAmountCcy1': None, 'executedAmountCcy2': None, 'requestedAmountCcy1': '0.00057328', 'requestedAmountCcy2': None, 'feeAmount': '0.00000000', 'feeCurrency': 'USD', 'price': '26200.0', 'averagePrice': None, 'clientCreateTimestamp': 1692594090681, 'serverCreateTimestamp': 1692594091638, 'lastUpdateTimestamp': 1692594091829, 'expireTime': None, 'effectiveTime': None}]}
        from trade_data.db.connection import DBConnect
        conn = DBConnect().getConnect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT id, unix_date, base,quote,side, orderType, amount, price FROM IM_ACTIVE_ORDERS")
        rows = res.fetchall()
        l_orders = []
        for row in rows:
            id, unix_date, base, quote, side, orderType, amount, price = row
            order_i = {'orderId': id
                , 'clientOrderId': None
                , 'clientId': 'user'
                , 'accountId': None
                , 'status': 'NEW'
                , 'statusIsFinal': False
                , 'currency1': base
                , 'currency2': quote
                , 'side': side
                , 'orderType': orderType
                , 'timeInForce': 'GTC'
                , 'comment': None
                , 'rejectCode': None
                , 'rejectReason': None
                , 'initialOnHoldAmountCcy1': amount
                , 'initialOnHoldAmountCcy2': None
                , 'executedAmountCcy1': None
                , 'executedAmountCcy2': None
                , 'requestedAmountCcy1': amount
                , 'requestedAmountCcy2': None
                , 'feeAmount': '0.00000000'
                , 'feeCurrency': quote
                , 'price': price
                , 'averagePrice': None
                , 'clientCreateTimestamp': unix_date
                , 'serverCreateTimestamp': None
                , 'lastUpdateTimestamp': None
                , 'expireTime': None
                , 'effectiveTime': None}
            l_orders.append(order_i)

        orders ={'ok': 'ok', 'data': l_orders}
        return orders


    def get_order(self, order_id):
        return self.api_call('get_order', {'id': order_id})



    def order_book(self, params={'pair':'BTC-USD'}):
        return self.api_call('get_order_book',params)



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

        # {'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '167916', 'clientOrderId': '1691909475451', 'accountId': '', 'status': 'NEW', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'SELL', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00050000', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'New', 'executionId': '1691752724241_100_3167', 'transactTime': '2023-08-13T06:51:16.901Z', 'expireTime': None, 'effectiveTime': None, 'price': '30000.0', 'averagePrice': None, 'feeAmount': '0.00000000', 'feeCurrency': 'USD', 'clientCreateTimestamp': 1691909475451, 'serverCreateTimestamp': 1691909476783, 'lastUpdateTimestamp': 1691909476896}}

        pairs = market.split('/')
        p1 = pairs[0]
        p2 = pairs[1]
        unix_dt = int(datetime.now().timestamp())  #выводит по времени UTC+0

        # CHECK BALANCE
        from trade_data.db.connection import DBConnect
        conn = DBConnect().getConnect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT AMOUNT FROM IM_BALANCE WHERE CURR = ?", (p1,))
        row = res.fetchone()
        balance_sum = row[0]

        transactTime = datetime.utcfromtimestamp((self.unix_curr_time + 2000) / 1000).strftime('%Y-%m-%dT%H:%M:%S.') + f'{(self.unix_curr_time + 2000) % 1000:03d}Z'

        from perfomance.cache.values import ValuesOrder
        ValuesOrder.orderId = ValuesOrder.orderId + 1  # Нумерация ордеров для режима эмуляции


        res = {'ok': 'ok', 'data': {'messageType': 'executionReport'
            , 'clientId': self.username
            , 'orderId': ValuesOrder.orderId
            , 'clientOrderId': self.unix_curr_time
            , 'accountId': ''
            , 'status': 'NEW'
            , 'currency1': pairs[0]
            , 'currency2': pairs[1]
            , 'side': 'SELL'
            , 'executedAmountCcy1': '0.00000000'
            , 'executedAmountCcy2': '0.00000000'
            , 'requestedAmountCcy1': amount
            , 'requestedAmountCcy2': None
            , 'orderType': 'Limit'
            , 'timeInForce': 'GTC'
            , 'comment': None
            , 'executionType': 'New'
            , 'executionId': f'{str(self.unix_curr_time)}_X_{ValuesOrder.orderId}'# Просто число. Логика формирования не понятна. Но и не нужна
            , 'transactTime': transactTime
            , 'expireTime': None
            , 'effectiveTime': None
            , 'price': price
            , 'averagePrice': None
            , 'feeAmount': '0.00000000'
            , 'feeCurrency': pairs[1]  # USD
                                    }}

        reject = False

        if amount < BASE_MIN:
            res['data']['status'] = 'REJECTED'
            res['data']['executionType'] = 'Rejected'
            res['data']['orderId'] = None
            res['data']['feeAmount'] = None
            res['data']['feeCurrency'] = None

            res['data'][
                'orderRejectReason'] = f'{{"code":414,"reason":"minOrderAmountCcy1 check failed. amountCcy1 {amount} is less than minOrderAmountCcy1 {BASE_MIN}"}}'
            res['data']['rejectCode'] = 414
            res['data'][
                'rejectReason'] = f'minOrderAmountCcy1 check failed. amountCcy1 {amount} is less than minOrderAmountCcy1 {BASE_MIN}'

            reject = True

        if balance_sum < amount:
            res['data']['status'] = 'REJECTED'
            res['data']['executionType'] = 'Rejected'
            res['data']['orderId'] = None
            res['data']['feeAmount'] = None
            res['data']['feeCurrency'] = None

            res['data']['orderRejectReason'] = '{"code":403,"reason":"Insufficient funds"}'
            res['data']['rejectCode'] = 403
            res['data']['rejectReason'] = 'Insufficient funds'

        if reject:
            conn.close()
            return res

        else:
            # Меняем статус в таблицы IM_BALANCE и IM_ACTIVE_ORDERS
            balance_state(res['data'], client_side=False, algo_nm=None, conn=conn)

            conn.commit()
            conn.close()
            return res



    def buy_limit_order(self, amount, price, clientOrderId=None, market='BTC/USD'):

        """ко времени self.unix_curr_time добавляется несколько секунд.
        Т.к. на самом деле, время транзакции происходит с задержкой"""

        # {'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': 'NONE', 'clientOrderId': '1689533205841', 'accountId': '', 'status': 'REJECTED', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00032900', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'Rejected', 'executionId': '1689360312873_101_8149', 'transactTime': '2023-07-16T18:46:46.926Z', 'expireTime': None, 'effectiveTime': None, 'price': '30302.9', 'averagePrice': None, 'feeAmount': None, 'feeCurrency': None, 'orderRejectReason': '{"code":414,"reason":"minOrderAmountCcy1 check failed. amountCcy1 0.00032900 is less than minOrderAmountCcy1 0.00042277"}', 'rejectCode': 414, 'rejectReason': 'minOrderAmountCcy1 check failed. amountCcy1 0.00032900 is less than minOrderAmountCcy1 0.00042277', 'clientCreateTimestamp': 1689533205, 'serverCreateTimestamp': 1689533206918}}
        # {'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': 'NONE', 'clientOrderId': '1689533367604', 'accountId': '', 'status': 'REJECTED', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'Rejected', 'executionId': '1689360312873_101_8152', 'transactTime': '2023-07-16T18:49:29.748Z', 'expireTime': None, 'effectiveTime': None, 'price': '30100.0', 'averagePrice': None, 'feeAmount': None, 'feeCurrency': None, 'orderRejectReason': '{"code":424,"reason":"ClientTime should be within 300000 ms timeframe. But difference was 1687843836379 ms. ClientTime 19700120-13:18:53.367, ServerTime 20230716-18:49:29.746"}', 'rejectCode': 424, 'rejectReason': 'ClientTime should be within 300000 ms timeframe. But difference was 1687843836379 ms. ClientTime 19700120-13:18:53.367, ServerTime 20230716-18:49:29.746', 'clientCreateTimestamp': 1689533367, 'serverCreateTimestamp': 1689533369738}}
        # {'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '114360', 'clientOrderId': '1689533488860', 'accountId': '', 'status': 'NEW', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'New', 'executionId': '1689360312873_101_8153', 'transactTime': '2023-07-16T18:51:30.071Z', 'expireTime': None, 'effectiveTime': None, 'price': '30100.0', 'averagePrice': None, 'feeAmount': '0.00000000', 'feeCurrency': 'USD', 'clientCreateTimestamp': 1689533488860, 'serverCreateTimestamp': 1689533489970, 'lastUpdateTimestamp': 1689533490064}}
        # {'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '114372', 'clientOrderId': '1689533832780', 'accountId': '', 'status': 'REJECTED', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'Rejected', 'executionId': '1689360312346_100_7727', 'transactTime': '2023-07-16T18:57:14.241Z', 'expireTime': None, 'effectiveTime': None, 'price': '30100.0', 'averagePrice': None, 'feeAmount': None, 'feeCurrency': None, 'orderRejectReason': '{"code":403,"reason":"Insufficient funds"}', 'rejectCode': 403, 'rejectReason': 'Insufficient funds', 'clientCreateTimestamp': 1689533832780, 'serverCreateTimestamp': 1689533834141, 'lastUpdateTimestamp': 1689533834233}}

        pairs = market.split('/')
        p1 = pairs[0]
        p2 = pairs[1]

        #CHECK BALANCE
        from trade_data.db.connection import DBConnect
        conn = DBConnect().getConnect()
        cursor = conn.cursor()
        res = cursor.execute("SELECT AMOUNT FROM IM_BALANCE WHERE CURR = ?",(p2,))
        row = res.fetchone()
        balance_sum = row[0]


        need_x = X_for_buyBTC(amount, price) # с учетом комиссии

        transactTime = datetime.utcfromtimestamp((self.unix_curr_time + 2000) / 1000).strftime('%Y-%m-%dT%H:%M:%S.') + f'{(self.unix_curr_time + 2000) % 1000:03d}Z'
        #unix_dt = int(datetime.now().timestamp() * 1000)  #выводит по времени UTC+0

        from perfomance.cache.values import ValuesOrder
        ValuesOrder.orderId = ValuesOrder.orderId + 1 #Нумерация ордеров для режима эмуляции


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
                , 'executionId': f'{str(self.unix_curr_time)}_X_{ValuesOrder.orderId}' # Просто число. Логика формирования не понятна. Но и не нужна
                , 'transactTime': transactTime
                , 'expireTime': None
                , 'effectiveTime': None
                , 'price': price
                , 'averagePrice': None
                , 'feeAmount': '0.00000000'
                , 'feeCurrency': pairs[1]  # USD
                                    }}

        reject = False
        if amount < BASE_MIN:
            res['data']['status'] = 'REJECTED'
            res['data']['executionType'] = 'Rejected'
            res['data']['orderId'] = None
            res['data']['feeAmount'] = None
            res['data']['feeCurrency'] = None


            res['data']['orderRejectReason'] = f'{{"code":414,"reason":"minOrderAmountCcy1 check failed. amountCcy1 {amount} is less than minOrderAmountCcy1 {BASE_MIN}"}}'
            res['data']['rejectCode'] = 414
            res['data']['rejectReason'] = f'minOrderAmountCcy1 check failed. amountCcy1 {amount} is less than minOrderAmountCcy1 {BASE_MIN}'

            reject = True


        if balance_sum < need_x:
            res['data']['status'] = 'REJECTED'
            res['data']['executionType'] = 'Rejected'
            res['data']['orderId'] = None
            res['data']['feeAmount'] = None
            res['data']['feeCurrency'] = None

            res['data']['orderRejectReason'] = '{"code":403,"reason":"Insufficient funds"}'
            res['data']['rejectCode'] = 403
            res['data']['rejectReason'] = 'Insufficient funds'

            reject = True

        res['data']['clientCreateTimestamp'] = self.unix_curr_time
        res['data']['serverCreateTimestamp'] = self.unix_curr_time + 1000
        res['data']['lastUpdateTimestamp'] = self.unix_curr_time + 10000


        if reject:
            conn.close()
            return res

        else:
            # Меняем статус в таблицы IM_BALANCE и IM_ACTIVE_ORDERS
            balance_state(res['data'], client_side=False, algo_nm=None, conn=conn)

            conn.commit()
            conn.close()
            return res



    def cancel_order(self, OrderId):

        unix_dt = int(datetime.now().timestamp()*1000)

        from trade_data.db.connection import DBConnect
        conn = DBConnect().getConnect()
        cursor = conn.cursor()

        conn.commit()
        conn.close()






    def cancel_all_order(self):
        param = {}
        return self.api_call('do_cancel_all_orders',param)


if __name__ == '__main__':
    from datetime import datetime

    api = EmulatorApi('test_user', 1689533488861)
    api.buy_limit_order(0.005,30000)

    #dt = datetime.fromtimestamp(1689533488)
    dt = datetime.utcfromtimestamp(1689533488860/1000).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    dt2 = datetime.utcfromtimestamp(1689533488860 / 1000).strftime('%Y-%m-%dT%H:%M:%S.')+f'{1689533488860 % 1000:03d}Z'

    formatted_datetime_with_milliseconds = dt[:-1] + f"{1689533488860 % 1000:03d}Z"
    print(dt)
    print(dt2)