# -*- coding: utf-8 -*-

import numpy as np

#Ввод на депозит



#x - сумма, которая тратится (с карты)
def X_to_DEPO(x, percent, fix):
    comis = x*percent/100+fix # процент берется от того, что тратится
    x_dep = round(x-comis,2)  # сумма, которая будет на депозите
    # print('xd=',comis)
    return x_dep          # Будет на депозите.   Проверена



#Вывод
def X_WITHD(x,percent,fix):
    comis = x * percent / 100 + fix
    return np.round(x - comis,2)



#Необходимо на депозите, чтобы вывести X
def Xdepo_for_Xout(Xout,percent,fix):
    depoX = (Xout+fix)/(1-percent/100)
    return depoX






if __name__ == '__main__':

    #r = X_to_DEPO(75.19, 2.99, 0)
    r= Xdepo_for_Xout(1000,3,50)
    print(r)