


def get_new_data(mode,pair,curr_time=None):

    p1,p2 = pair.split('/')
    if mode == 'TEST':
        from emulatorApi import customApi

        #do request to src

        res = data.history(p1,p1)
        #save data into db

        #or save into Memory



    else:
        from api import customApi

        # do request to src
        # save data into db

    return None

