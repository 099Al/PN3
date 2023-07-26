from db import queriesDB as qdb

valid_pairs = ['BTC/USD']

def get_new_data(mode,pair,curr_time=None):

    if pair not in valid_pairs:
        print('Not valid pair')
        exit()

    p1,p2 = pair.split('/')


    if mode == 'TEST':

        from emulatorApi.cexioEmNewApi import emulatorApi

        #Делается запрос к источнику(либо к сайту, либо к эмулятору)
        emApi = emulatorApi(curr_time)
        #emApi.currentTime=curr_time  #Вслучае эмуляции ставим время, в которое делается запрос

        res = emApi.trade_history(f'{p1}-{p2}')
        print(res)

        exit()


        #save data into db  #or save into Memory #Запись в cache реализовывать в функйии не отдельно
        qdb.save_history_tik(res)


    if mode == 'TRAID':
        from api.cexioNewApi import Api

        api = Api(config.API_USER, config.API_KEY, config.API_SECRET)

        res = api.trade_history(f'{p1}-{p2}')

        print('curr',res)


    return None

