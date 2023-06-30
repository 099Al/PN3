# -*- coding: utf-8 -*-


#Оставить n знаков после запятой
def cutX(x,n):
    s = str(x)
    x = s[0:s.index('.')+n+1]  # оставить только n знаков после ,
    return float(x)