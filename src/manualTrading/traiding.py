import asyncio

from src.api.cexio.cexioNewApi import Api
from src.config import prj_configs

if __name__ == '__main__':


    api = Api(username=prj_configs.API_USER,
                api_key=prj_configs.API_KEY,
                api_secret=prj_configs.API_SECRET,
                account_id='trade_test'
              )


    #res = asyncio.run(api.create_account("trade_test", "BTC"))

    #res = asyncio.run(api.cancel_order(2690120))

    res = asyncio.run(api.current_prices(pair='BTC/USD'))
    print(res)

    # res = asyncio.run(api.archived_orders())

    #res = asyncio.run(api.cancel_order(OrderId=2690184))
    #print(res)

    #res = asyncio.run(api.set_order(amount=0.00019425, price=66800, sell_buy='BUY'))

    # res = asyncio.run(api.set_order(amount=0.00019, price=67000.0, sell_buy='SELL'))
    print(res)

    #print( int(datetime.now().timestamp() * 1000) )

    res = asyncio.run(api.open_orders(accountId='trade_test'))
    print('orders', res)

    res = asyncio.run(api.account_status(accountId='trade_test'))
    print(res)

    #res = asyncio.run(api.trade_history())

    #res = asyncio.run(api.get_myfee())

    res = asyncio.run(api.transaction_history(accountId='trade_test'))
    print('transactions',res)

    # {'bestBid': '68560.6', 'bestAsk': '68579.6'}
    # {'bestBid': '68160.6', 'bestAsk': '68175.5'}
    # {'bestBid': '68093.5', 'bestAsk': '68110.6'}
    # {'bestBid': '67488.7', 'bestAsk': '67510.6'}