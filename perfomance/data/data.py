from db import queriesDB as qdb

valid_pairs = ['BTC/USD']

def get_new_data(mode,pair,curr_time=None):

    if pair not in valid_pairs:
        print('Not valid pair')
        exit()

    p1,p2 = pair.split('/')


    if mode == 'TEST':
        from emulatorApi.publicApi import CustomApi

        #Делается запрос к источнику(либо к сайту, либо к эмулятору)
        customApi=CustomApi()
        customApi.currentTime=curr_time  #Вслучае эмуляции ставим время, в которое делается запрос

        res = customApi.history(p1,p1)

        #save data into db  #or save into Memory #Запись в cache реализовывать в функйии не отдельно
        qdb.save_history_tik(res)


    if mode == 'TRAID':
        from api.publicApi import CustomApi

        customApi = CustomApi()
        res = customApi.history(p1,p2)

        print('curr',res)


    return None

