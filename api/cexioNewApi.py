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
            signature = self.__signature(now_stamp,command,param)
            headers = {
                'X-AGGR-KEY': self.api_key,
                'X-AGGR-TIMESTAMP': str(now_stamp),
                'X-AGGR-SIGNATURE': signature,
                'Content-Type': 'application/json'
                #'User-Agent': 'client'
            }

            request_url = (BASE_PRIVATE_URL % command)

            #print(request_url)

        result = self.__post(request_url,param,headers)

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



    api = Api(config.API_USER, config.API_KEY, config.API_SECRET)

    buy_req = api.buy_limit_order(0.00042277, 28000.0, 1)

    print(buy_req)

    exit()

    # test public
    #currencies_info = api.currencies_info()

    #fromDT = int(datetime.now().timestamp())-3600*2
    #toDT = int(datetime.now().timestamp()) - 5
    #currencies_info = api.candles(dataType='bestAsk',fromDT=fromDT,toDT=toDT)
    #print(currencies_info)

    trade_hist = api.trade_history()


    # test private
    #balance = api.balance()
    #status = api.order_book()
    #print('status',status)
    #status {'ok': 'ok', 'data': {'timestamp': 1689533783192, 'currency1': 'BTC', 'currency2': 'USD', 'bids': [['30319.4', '0.00000170'], ['30299.1', '0.04792184'], ['30262.0', '0.60575455'], ['30261.9', '0.05555679'], ['30259.8', '0.01318177'], ['30257.5', '0.22923046'], ['30257.4', '0.06147200'], ['30257.2', '0.00495500'], ['30256.8', '0.60763352'], ['30256.3', '0.85733632'], ['30256.2', '0.03302380'], ['30255.1', '1.28020347'], ['30254.3', '0.05000000'], ['30254.1', '0.34297487'], ['30253.9', '0.26564482'], ['30253.3', '0.42525278'], ['30253.0', '0.84045613'], ['30252.4', '1.03842140'], ['30252.1', '0.03000000'], ['30251.6', '0.03000000'], ['30251.5', '0.20000000'], ['30251.1', '0.02000000'], ['30251.0', '0.03285173'], ['30250.9', '0.15210000'], ['30250.4', '0.32708969'], ['30250.3', '0.53181610'], ['30250.0', '0.61079404'], ['30249.7', '0.00826330'], ['30249.6', '0.02000000'], ['30249.5', '0.03000000'], ['30249.0', '0.05000000'], ['30248.8', '0.05000000'], ['30247.9', '0.14804958'], ['30247.8', '0.04000000'], ['30247.6', '0.04409990'], ['30247.1', '0.68102962'], ['30247.0', '0.00285223'], ['30246.9', '1.08000000'], ['30246.8', '0.29075238'], ['30246.0', '0.87577399'], ['30245.0', '1.96101931'], ['30244.7', '0.07007400'], ['30244.0', '0.66292683'], ['30242.0', '0.84467014'], ['30241.1', '0.00640716'], ['30241.0', '0.09887000'], ['30240.0', '0.55285311'], ['30239.0', '0.61109010'], ['30237.0', '2.31442186'], ['30236.0', '0.03000000'], ['30235.0', '2.02590566'], ['30234.0', '3.67452200'], ['30233.8', '0.00100000'], ['30233.0', '0.00285399'], ['30231.0', '3.46346513'], ['30229.3', '0.65000000'], ['30229.0', '2.79745224'], ['30228.1', '0.00522151'], ['30228.0', '1.16138642'], ['30227.6', '0.00635604'], ['30227.0', '0.09000000'], ['30226.5', '0.00061584'], ['30226.3', '0.00395340'], ['30226.0', '1.70214118'], ['30225.0', '3.68119395'], ['30224.0', '0.97390835'], ['30222.5', '0.06393747'], ['30222.0', '0.00285538'], ['30221.8', '0.63680000'], ['30221.0', '1.34601472'], ['30220.0', '0.00600000'], ['30219.8', '2.47833163'], ['30219.6', '0.18389739'], ['30219.2', '0.00124924'], ['30219.1', '1.06540284'], ['30219.0', '2.54630000'], ['30218.9', '0.06406552'], ['30218.0', '0.15285588'], ['30217.9', '0.00328911'], ['30217.8', '2.37881962'], ['30217.6', '0.11852617'], ['30217.5', '0.33039005'], ['30217.0', '5.13140960'], ['30216.7', '0.00409618'], ['30216.6', '2.38904443'], ['30216.5', '0.69967082'], ['30216.2', '2.53862764'], ['30216.0', '0.08006694'], ['30215.9', '0.01960000'], ['30215.6', '0.11770000'], ['30215.3', '0.00814189'], ['30215.2', '0.25188276'], ['30215.0', '0.00214222'], ['30214.9', '1.21837934'], ['30214.6', '0.33313271'], ['30214.5', '0.39409631'], ['30214.4', '0.00443850'], ['30214.3', '0.00003651'], ['30214.2', '0.35944654'], ['30214.1', '0.69476000'], ['30214.0', '3.76584124'], ['30213.6', '1.77611443'], ['30213.0', '2.35792154'], ['30211.9', '0.65000000'], ['30211.2', '0.39055345'], ['30211.1', '0.04945000'], ['30211.0', '0.00285676'], ['30210.9', '0.03670987'], ['30210.8', '0.00829552'], ['30210.2', '0.20550000'], ['30210.0', '3.16137189'], ['30209.9', '0.04000000'], ['30209.8', '0.00002001'], ['30209.6', '0.41736000'], ['30209.0', '1.74708000'], ['30208.9', '3.46825336'], ['30208.8', '0.65000000'], ['30208.7', '0.63237000'], ['30208.6', '1.16736000'], ['30208.5', '0.16262000'], ['30208.4', '0.29579181'], ['30208.1', '0.22987615'], ['30208.0', '0.00214288'], ['30207.7', '1.64245318'], ['30207.6', '5.19338842'], ['30207.2', '0.32388000'], ['30206.9', '0.10000000'], ['30206.6', '0.20577885'], ['30206.1', '0.13906038'], ['30206.0', '0.81596414'], ['30205.9', '0.19461002'], ['30205.8', '0.18638947'], ['30205.7', '0.32435000'], ['30205.5', '3.44693000'], ['30205.4', '0.00170000'], ['30205.3', '4.14944003'], ['30205.2', '0.05434000'], ['30205.0', '4.48387850'], ['30204.8', '0.71550005'], ['30204.7', '0.85966000'], ['30204.6', '0.18690000'], ['30204.5', '0.35857993'], ['30204.2', '0.32435000'], ['30204.1', '0.00034000'], ['30204.0', '0.03799384'], ['30203.9', '0.00330619'], ['30203.7', '0.00260000'], ['30203.6', '0.22020395'], ['30202.4', '0.65000000'], ['30202.3', '1.00760000'], ['30202.0', '1.36610812'], ['30201.2', '3.30647853'], ['30200.5', '0.00935285'], ['30200.4', '0.29103949'], ['30200.3', '0.00467383'], ['30200.2', '0.00128000'], ['30200.0', '6.40179802'], ['30199.9', '0.30875648'], ['30199.3', '0.65000000'], ['30198.0', '2.35090022'], ['30196.9', '0.22109351'], ['30196.8', '0.01234000'], ['30196.7', '0.00260000'], ['30196.6', '0.00170000'], ['30196.4', '0.55633000'], ['30196.3', '0.00100000'], ['30196.2', '0.65000000'], ['30196.1', '0.07700000'], ['30195.8', '0.25090000'], ['30195.7', '0.16694000'], ['30194.8', '5.52091197'], ['30193.5', '0.00251360'], ['30193.1', '0.65000000'], ['30192.8', '1.08345600'], ['30191.0', '0.55000000'], ['30189.5', '4.96163230'], ['30189.4', '0.65000000'], ['30188.8', '0.00087500'], ['30188.0', '0.20000000'], ['30187.9', '0.41819404'], ['30187.0', '0.33102519'], ['30184.0', '0.55000000'], ['30178.0', '0.56662252'], ['30172.0', '13.72979948'], ['30170.0', '7.04100000'], ['30169.5', '0.07345806'], ['30165.0', '0.55000000'], ['30163.0', '0.00100000'], ['30161.0', '0.55000000'], ['30156.0', '0.55000000'], ['30150.0', '0.55000000'], ['30143.0', '0.55000000'], ['30137.0', '0.55000000'], ['30132.0', '7.89589461'], ['30118.8', '0.00136049'], ['30112.7', '0.08543986'], ['30100.0', '0.10042277'], ['30084.2', '0.00200000'], ['30050.0', '0.01000000'], ['30048.7', '0.00200000'], ['30041.7', '0.11362366'], ['30016.9', '0.00200000'], ['30002.0', '0.05003673'], ['30000.0', '0.12555329'], ['29991.0', '0.00100000'], ['29990.0', '0.07245000'], ['29980.0', '0.10925757'], ['29978.4', '0.00200000'], ['29971.0', '0.02607000'], ['29969.0', '0.02607000'], ['29967.0', '0.02607000'], ['29966.0', '1.35754590'], ['29965.0', '0.73562054'], ['29964.0', '0.02607000'], ['29963.0', '0.21644000'], ['29962.0', '0.68639200'], ['29961.0', '0.02618000'], ['29960.0', '0.58557000'], ['29959.0', '0.02000000'], ['29958.0', '0.71342131'], ['29957.0', '0.11718982'], ['29956.0', '2.01849193'], ['29947.0', '0.15311149'], ['29942.6', '0.00200000'], ['29881.7', '0.00200000'], ['29821.0', '0.00200000'], ['29820.6', '0.20501431'], ['29750.0', '0.07258080'], ['29715.7', '0.00200000'], ['29655.3', '0.00200000'], ['29652.1', '0.27576476'], ['29650.0', '0.01160000'], ['29626.0', '0.00100000'], ['29595.0', '0.00200000'], ['29561.0', '0.00200000'], ['29501.0', '0.02000000'], ['29500.9', '0.00200000'], ['29500.0', '0.02000000'], ['29427.3', '0.37222677'], ['29400.0', '0.05322100'], ['29128.0', '0.50198431'], ['29111.0', '0.05000000'], ['29100.0', '0.00046297'], ['29000.0', '0.05530190'], ['28900.0', '0.01400000'], ['28889.0', '0.02031000'], ['28730.3', '0.68094097'], ['28700.0', '0.12043000'], ['28675.0', '0.00105000'], ['28202.6', '0.92761979']], 'asks': [['30319.5', '20.60564588'], ['30319.8', '4.40266571'], ['30325.6', '0.00840086'], ['30329.8', '9.02358258'], ['30345.9', '0.04788494'], ['30383.3', '0.05544573'], ['30426.5', '0.77708942'], ['30426.6', '0.06384659'], ['30444.0', '0.02500000'], ['30476.3', '0.07308755'], ['30500.0', '0.00100000'], ['30533.8', '0.08484876'], ['30600.0', '0.01000000'], ['30606.0', '0.11257163'], ['30700.0', '0.01844952'], ['30702.7', '0.15121562'], ['30750.0', '0.01540915'], ['30832.9', '0.20162083'], ['30900.0', '0.00850000'], ['30935.0', '0.00749363'], ['30950.0', '0.01000000'], ['31000.0', '0.00336060'], ['31008.1', '0.26966786'], ['31100.0', '0.01905709'], ['31245.0', '0.36123733'], ['31400.0', '0.25000000'], ['31500.0', '0.01319864'], ['31566.0', '0.48220983'], ['31590.0', '0.00756412'], ['31700.0', '0.08409939'], ['31800.0', '0.01000000'], ['31888.0', '0.01000000'], ['31900.0', '0.04721000'], ['32000.0', '0.35734055'], ['32003.0', '0.64518667'], ['32100.0', '0.01000000'], ['32222.0', '0.00010000'], ['32250.0', '0.01000000'], ['32300.0', '0.01900000'], ['32400.0', '0.02972389'], ['32500.0', '0.11000000'], ['32580.0', '0.01200000'], ['32600.0', '0.17582980'], ['32601.8', '0.86276916'], ['32611.0', '0.00184673'], ['32750.0', '0.01000000'], ['33000.0', '0.12814052'], ['33162.0', '0.00500000'], ['33251.0', '0.07552383'], ['33333.0', '0.05010000'], ['33429.3', '1.15343920'], ['33500.0', '1.47936719'], ['34000.0', '0.00442000']]}}

    orders = api.open_orders()
    print('orders',orders)

    ticker = api.ticker()
    ticker_btc = ticker['data']['BTC-USD']
    print(ticker_btc['bestBid'])
    print(ticker_btc['bestAsk'])
    print(int(datetime.now().timestamp() * 1000))

    #buy_req = api.buy_limit_order(0.00042277,30100.0,1)
    #{'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': 'NONE', 'clientOrderId': '1689533205841', 'accountId': '', 'status': 'REJECTED', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00032900', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'Rejected', 'executionId': '1689360312873_101_8149', 'transactTime': '2023-07-16T18:46:46.926Z', 'expireTime': None, 'effectiveTime': None, 'price': '30302.9', 'averagePrice': None, 'feeAmount': None, 'feeCurrency': None, 'orderRejectReason': '{"code":414,"reason":"minOrderAmountCcy1 check failed. amountCcy1 0.00032900 is less than minOrderAmountCcy1 0.00042277"}', 'rejectCode': 414, 'rejectReason': 'minOrderAmountCcy1 check failed. amountCcy1 0.00032900 is less than minOrderAmountCcy1 0.00042277', 'clientCreateTimestamp': 1689533205, 'serverCreateTimestamp': 1689533206918}}
    #{'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': 'NONE', 'clientOrderId': '1689533367604', 'accountId': '', 'status': 'REJECTED', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'Rejected', 'executionId': '1689360312873_101_8152', 'transactTime': '2023-07-16T18:49:29.748Z', 'expireTime': None, 'effectiveTime': None, 'price': '30100.0', 'averagePrice': None, 'feeAmount': None, 'feeCurrency': None, 'orderRejectReason': '{"code":424,"reason":"ClientTime should be within 300000 ms timeframe. But difference was 1687843836379 ms. ClientTime 19700120-13:18:53.367, ServerTime 20230716-18:49:29.746"}', 'rejectCode': 424, 'rejectReason': 'ClientTime should be within 300000 ms timeframe. But difference was 1687843836379 ms. ClientTime 19700120-13:18:53.367, ServerTime 20230716-18:49:29.746', 'clientCreateTimestamp': 1689533367, 'serverCreateTimestamp': 1689533369738}}
    #{'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '114360', 'clientOrderId': '1689533488860', 'accountId': '', 'status': 'NEW', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'New', 'executionId': '1689360312873_101_8153', 'transactTime': '2023-07-16T18:51:30.071Z', 'expireTime': None, 'effectiveTime': None, 'price': '30100.0', 'averagePrice': None, 'feeAmount': '0.00000000', 'feeCurrency': 'USD', 'clientCreateTimestamp': 1689533488860, 'serverCreateTimestamp': 1689533489970, 'lastUpdateTimestamp': 1689533490064}}
    #{'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '114372', 'clientOrderId': '1689533832780', 'accountId': '', 'status': 'REJECTED', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'Rejected', 'executionId': '1689360312346_100_7727', 'transactTime': '2023-07-16T18:57:14.241Z', 'expireTime': None, 'effectiveTime': None, 'price': '30100.0', 'averagePrice': None, 'feeAmount': None, 'feeCurrency': None, 'orderRejectReason': '{"code":403,"reason":"Insufficient funds"}', 'rejectCode': 403, 'rejectReason': 'Insufficient funds', 'clientCreateTimestamp': 1689533832780, 'serverCreateTimestamp': 1689533834141, 'lastUpdateTimestamp': 1689533834233}}
    #{'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '114374', 'clientOrderId': '1689533870474', 'accountId': '', 'status': 'REJECTED', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'Rejected', 'executionId': '1689360312873_101_8161', 'transactTime': '2023-07-16T18:57:51.698Z', 'expireTime': None, 'effectiveTime': None, 'price': '30100.0', 'averagePrice': None, 'feeAmount': None, 'feeCurrency': None, 'orderRejectReason': '{"code":403,"reason":"Insufficient funds"}', 'rejectCode': 403, 'rejectReason': 'Insufficient funds', 'clientCreateTimestamp': 1689533870474, 'serverCreateTimestamp': 1689533871582, 'lastUpdateTimestamp': 1689533871678}}

    #
    #2023-08-07 10:22  {'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '159410', 'clientOrderId': '1691382131250', 'accountId': '', 'status': 'NEW', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'New', 'executionId': '1691079661474_101_7342', 'transactTime': '2023-08-07T04:22:13.513Z', 'expireTime': None, 'effectiveTime': None, 'price': '29000.0', 'averagePrice': None, 'feeAmount': '0.00000000', 'feeCurrency': 'USD', 'clientCreateTimestamp': 1691382131250, 'serverCreateTimestamp': 1691382133405, 'lastUpdateTimestamp': 1691382133504}}
    #2023-08-07 10:24  {'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '159411', 'clientOrderId': '1691382230740', 'accountId': '', 'status': 'NEW', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'New', 'executionId': '1691079661474_101_7345', 'transactTime': '2023-08-07T04:23:52.974Z', 'expireTime': None, 'effectiveTime': None, 'price': '28000.0', 'averagePrice': None, 'feeAmount': '0.00000000', 'feeCurrency': 'USD', 'clientCreateTimestamp': 1691382230740, 'serverCreateTimestamp': 1691382232820, 'lastUpdateTimestamp': 1691382232969}}


    #print(buy_req)
    #status = api.open_orders()

    #orders: orders {'ok': 'ok', 'data': {'messageType': 'executionReport', 'clientId': 'up112344963', 'orderId': '114390', 'clientOrderId': '1689534446302', 'accountId': '', 'status': 'NEW', 'currency1': 'BTC', 'currency2': 'USD', 'side': 'BUY', 'executedAmountCcy1': '0.00000000', 'executedAmountCcy2': '0.00000000', 'requestedAmountCcy1': '0.00042277', 'requestedAmountCcy2': None, 'orderType': 'Limit', 'timeInForce': 'GTC', 'comment': None, 'executionType': 'New', 'executionId': '1689360312346_100_7759', 'transactTime': '2023-07-16T19:07:27.579Z', 'expireTime': None, 'effectiveTime': None, 'price': '30100.0', 'averagePrice': None, 'feeAmount': '0.00000000', 'feeCurrency': 'USD', 'clientCreateTimestamp': 1689534446302, 'serverCreateTimestamp': 1689534447479, 'lastUpdateTimestamp': 1689534447572}}

    #cancel_order = api.cancel_order(1689534446302)
    #print('cancel_order',cancel_order)
    #cancel_order {'ok': 'ok', 'data': {}}  OK-отменен

    cancel_all = api.cancel_all_order()
    print(cancel_all)
    #{'ok': 'ok', 'data': {'clientOrderIds': ['1689534607845']}}


