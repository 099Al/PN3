# -*- coding: utf-8 -*-


#stopSignal
'''
STOP_TYPE - тип стопа
1 - #Если хотя бы один из набора, ниже цены, то срабатывает
2 - #Если все ниже цены, то срабатывает
3 - #Если k показателей ниже цены
4 - #Если k последних показателей ниже цены
STOP_K - параметр k длятипа 3 и 4
'''

#reset
STOP_TYPE = 1
STOP_K = 3
STOP_LIMIT_1 = True   #учитывать 1-й лимит