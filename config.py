# -*- coding: utf-8 -*-

import os



def getPathDB(dir=None):
    if dir == None:
        basedir = os.path.abspath(os.path.dirname(__file__))
    else:
        basedir = dir
    path = os.path.join(basedir,'PN3_db.db')
    return path


def commission():
    pass

def price():
    pass



if __name__ == '__main__':
    print(getPathDB())
