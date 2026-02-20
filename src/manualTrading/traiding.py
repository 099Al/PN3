import asyncio
import json
from typing import Any

from src.api.cexio.cexioNewApi import Api
from src.config import prj_configs

def pretty(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == '__main__':


    api = Api(username=prj_configs.API_USER,
                api_key=prj_configs.API_KEY,
                api_secret=prj_configs.API_SECRET,
                account_id='trade_test'
              )


    #res = asyncio.run(api.create_account("trade_test", "BTC"))

    #res = asyncio.run(api.cancel_order(2698762))

    res = asyncio.run(api.current_prices(pair='BTC/USD'))
    print(res)

    # res = asyncio.run(api.archived_orders())

    # res = asyncio.run(api.cancel_order(OrderId=2698772))
    #print(res)

    #res = asyncio.run(api.set_order(amount=0.00022332, price=67000, sell_buy='BUY'))

    #res = asyncio.run(api.set_order(amount=0.00022142, price=68110.0, sell_buy='SELL'))
    print(res)

    #print( int(datetime.now().timestamp() * 1000) )

    res = asyncio.run(api.open_orders(accountId='trade_test'))
    print('orders', res)

    res = asyncio.run(api.account_status(accountId='trade_test'))
    pretty((res))

    #res = asyncio.run(api.trade_history())

    #res = asyncio.run(api.get_myfee())

    res = asyncio.run(api.transaction_history(accountId='trade_test'))
    print('transactions',res)

    # {'bestBid': '68560.6', 'bestAsk': '68579.6'}
    # {'bestBid': '68160.6', 'bestAsk': '68175.5'}
    # {'bestBid': '68093.5', 'bestAsk': '68110.6'}
    # {'bestBid': '67488.7', 'bestAsk': '67510.6'}

    # ---btc max = 0.00022332  price = 67000  x = 15.00
    # "USD": {
    #     "balance": "19.69232091",
    #     "balanceOnHold": "14.99984610",
    #     "balanceAvailable": "4.69247481",
    #     "balanceInConvertedCurrency": "19.69232091"