from db import queriesDB as qdb

valid_pairs = ['BTC/USD']

def get_new_data(mode,pair,curr_time=None):

    if pair not in valid_pairs:
        print('Not valid pair')
        exit()

    p1,p2 = pair.split('/')


    if mode == 'TEST':
        from emulatorApi.customApi import CustomApi

        #Делается запрос к источнику(либо к сайту, либо к эмулятору)
        customApi=CustomApi()
        customApi.currentTime=curr_time  #Вслучае эмуляции ставим время, в которое делается запрос

        res = customApi.history(p1,p1)

        #save data into db
        from db.connection import DBConnect
        conn = DBConnect().getConnect()
        qdb.save_history_tik(conn,res)
        conn.close()

        #or save into Memory



    else:
        from api.customApi import CustomApi

        customApi = CustomApi()
        res = customApi.history(p1,p2)

        print('curr',res)


    return None

