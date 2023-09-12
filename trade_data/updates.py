from configs import config

from trade_data import queriesDB as qdb

valid_pairs = ['BTC/USD']

def get_new_data(mode,pair,curr_time=None):

    if pair not in valid_pairs:
        print('Not valid pair')
        exit()

    p1,p2 = pair.split('/')


    if mode == 'TEST':
        from api.emulatorcexio.cexioEmNewApi import emulatorApi
        #Делается запрос к источнику(либо к сайту, либо к эмулятору)
        api = emulatorApi(curr_time)
        #emApi.currentTime=curr_time  #В случае эмуляции ставим время, в которое делается запрос
    if mode == 'TRAID':
        from api.cexio.cexioNewApi import Api
        api = Api(config.API_USER, config.API_KEY, config.API_SECRET)


    res = api.trade_history(f'{p1}-{p2}')
    tiks = res['data']['trades']

    # save _data into trade_data  #or save into Memory ?
    qdb.save_history_tik(tiks)

    print('curr',res)

    return None

def check_ordrs():
