# -*- coding: utf-8 -*-



import PN3.function.exchangeFunction as exchf

import PN3.function.transacFunction as transf
import PN3.deposit.depoMoneyInOut as depof
from   PN3.util.calcUtil import cutX

#dtime = unix_to_date(p.get('timestamp'))

# GET PARAMETERS FEE DEPOSIT CURRENCY
# FOR USD RUB BTC

'''
r: rub
pr: price
'''

class InfoCalcFromDep():

    def __init__(self):

        from PN3.configs.feeslimits.constant import com_out_pr_u,com_out_f_u #Комиссия вывод USD
        from PN3.configs.feeslimits.constant import com_out_pr_r,com_out_f_r #Комиссия вывод RUB
        from PN3.configs.feeslimits.constant import com_in_pr_u,com_in_f_u   # Комиссия ввод USD
        from PN3.configs.feeslimits.constant import com_in_pr_r, com_in_f_r  # Комиссия ввод RUB
        from PN3.configs.feeslimits.constant import limit_usd,limit_rub


        self.u_out_dep_prc = com_out_pr_u
        self.u_out_dep_fix = com_out_f_u

        self.r_out_dep_prc = com_out_pr_r
        self.r_out_dep_fix = com_out_f_r

        self.u_in_dep_prc = com_in_pr_u
        self.u_in_dep_fix = com_in_f_u

        self.r_in_dep_prc = com_in_pr_r
        self.r_in_dep_fix = com_in_f_r



        self.limit_usd=limit_usd
        self.limit_rub=limit_rub

    def setCurr(self,usd_b,usd_s):
        self.usd_b = usd_b
        self.usd_s= usd_s

    def setOldCurr(self,usd_b,usd_s):
        self.old_usd_b = usd_b
        self.old_usd_s= usd_s

    def setUsdPrmt(self,price_tosell_btcusd,price_tobuy_btcusd,maker_taker,taker):
        self.price_tosell_btcusd=price_tosell_btcusd
        self.price_tobuy_btcusd = price_tobuy_btcusd
        self.mk_tk_usd = maker_taker
        self.taker = taker

    def setRubPrmt(self, price_tosell_btcrub,price_tobuy_btcrub, maker_taker):
        self.price_tosell_btcrub = price_tosell_btcrub
        self.price_tobuy_btcrub = price_tobuy_btcrub
        self.mk_tk_rub = maker_taker

    # Заполнение депозита
    def setDepoBalance(self, x_usd=0, x_rub=0, btc=0):
            self.x_usd = x_usd
            self.x_rub = x_rub
            self.btc = btc

    #Доп. сумма с карты на баланс
    def setAddX(self,add_usd,add_rub):
        self.add_usd=add_usd
        self.add_rub=add_rub



    #Вывод USD с депозита
    #add USD дополнительный ввод USD на депозит, который тоже будет выводится вместе с суммой usd
    #add RUB дополнительный ввод RUB на депозит
    def USD_OUT(self):

        add_usd_d =0
        if(self.add_usd>0):
            add_usd_d = depof.X_to_DEPO(self.add_usd, self.u_in_dep_prc, self.u_in_dep_fix) #уйдет на депозит

        usd = self.x_usd+add_usd_d
        usd_out = depof.X_WITHD(usd,self.u_out_dep_prc,self.u_out_dep_fix)  #USD на карте

        rub_x = exchf.sellUSD(usd_out,self.usd_b)    #Перевод в RUB
        rub_x2 = exchf.sellUSD(usd_out, self.old_usd_b)  # Перевод в RUB

        return{'x':usd
               ,'add_usd':self.add_usd
               ,'add_usd_dep':add_usd_d
               ,'usd_out':usd_out
               ,'rub':rub_x
               ,'rub2':rub_x2}


    def RUB_OUT(self):
        '''Вывод с депозита RUB'''

        add_rub_x = 0

        if (self.add_rub > 0):
            add_rub_x = depof.X_to_DEPO(self.add_rub, self.r_in_dep_prc, self.r_in_dep_fix)

        rub = self.x_rub + add_rub_x
        rub_out = depof.X_WITHD(rub, self.r_out_dep_prc, self.r_out_dep_fix)  # RUB на карте

        usd_r = exchf.buyUSD(rub_out, self.usd_s)
        usd_r2 = exchf.buyUSD(rub_out, self.old_usd_s)

        return {'x': rub
            , 'add_rub': self.add_rub
            , 'add_rub_x': add_rub_x
            , 'rub_out': rub_out
            , 'usd': usd_r
            , 'usd2': usd_r2}






    def USD_btc_rub_OUT(self):
        '''Вывод с депозита USD, предварительно переведя в RUB'''

        add_usd_x = 0
        add_rub_x = 0

        if (self.add_usd > 0):
            add_usd_x = depof.X_to_DEPO(self.add_usd, self.u_in_dep_prc, self.u_in_dep_fix)
        if (self.add_rub > 0):
            add_rub_x = depof.X_to_DEPO(self.add_rub, self.r_in_dep_prc, self.r_in_dep_fix)

        #Второй вариант вывода
        usd = self.x_usd + add_usd_x
        btc = transf.buyBTC(usd,self.price_tobuy_btcusd,self.mk_tk_usd)
        btc_max = btc['btc']          #максимольное кол-во BTC
        dx = btc['dx']                #Остаток USD
        btc_sum = btc_max+self.btc

        btc_pre = transf.presellBTC(btc_sum, self.price_tosell_btcrub)
        rub = transf.sellBTC(btc_pre,self.price_tosell_btcrub,self.mk_tk_rub)['x']

        rub = rub+add_rub_x+self.x_rub

        rub_out = depof.X_WITHD(rub,self.r_out_dep_prc,self.r_out_dep_fix)             #На карте

        usd_r = exchf.buyUSD(rub_out,self.usd_s)  #Перевести в USD на карте
        usd_r_old = exchf.buyUSD(rub_out, self.old_usd_s)  # Перевести в USD на карте

        return{ 'usd':usd
                ,'btc_max':btc_max
                ,'dx':dx
                ,'btc_sum':btc_sum
                ,'btc_pre':btc_pre
                ,'mk_tk_rub':self.mk_tk_rub
                ,'rub':rub
                ,'rub_add':add_rub_x
                ,'rub_resed':self.x_rub
                ,'rub_out':rub_out
                ,'usd_r':usd_r
                ,'usd_r_old':usd_r_old}





    def RUB_btc_usd_OUT(self,add_rub=0,add_usd=0):
        '''Вывод с депозита RUB, предварительно переведя в USD'''

        add_usd_x = 0
        add_rub_x = 0

        if (add_usd > 0):
            add_usd_x = depof.X_to_DEPO(add_usd, self.u_in_dep_prc, self.u_in_dep_fix)
        if (add_rub > 0):
            add_rub_x = depof.X_to_DEPO(add_rub, self.r_in_dep_prc, self.r_in_dep_fix)

        rub = self.x_rub + add_rub_x

        btc = transf.buyBTC(rub,self.price_tobuy_btcrub)
        btc_max = btc['btc']  # максимольное кол-во BTC
        dx = btc['dx']  # Остаток RUB
        btc_sum = btc_max+self.btc


        btc_pre = transf.presellBTC(btc_max, self.price_tosell_btcusd)
        usd = transf.sellBTC(btc_pre,self.price_tosell_btcusd,self.mk_tk_usd)
        usd = usd+add_usd_x+self.x_usd
        usd_out = depof.X_WITHD(usd,self.u_out_dep_prc,self.u_out_dep_fix)  # USD на карте

        rub_u = exchf.sellUSD(usd_out, self.usd_b)  # Перевод в RUB
        rub_u2 = exchf.sellUSD(usd_out, self.old_usd_b)

        return {'rub': rub
            , 'btc_max': btc_max
            , 'dx': dx
            , 'btc_sum':btc_sum
            , 'btc_pre': btc_pre
            , 'usd': usd
            , 'usd_add':add_usd_x
            , 'usd_resed':self.x_usd
            , 'usd_out': usd_out
            , 'rub_u': rub_u
            , 'rub_u2': rub_u2}




    #сколько необходимо добавить RUB, Чтобы вывести в RUB
    def add_RUB_rub_out(self,depo_rub=-1):

        if(depo_rub==-1):
            rub = self.x_rub
        else:
            rub = depo_rub

        def d_deposit(r):
            return depof.X_to_DEPO(r, self.r_in_dep_prc, self.r_in_dep_fix)

        #rub -  сумма на депозите
        dx = 100
        st = 200
        e = 0.01
        d_dep = d_deposit(dx)
        #print('ddep=', d_dep, 'dx', dx)
        #Поиск идет через приближения
        #Можно и через решение линейного уравнения
        while d_dep+rub<self.limit_rub or d_dep+rub-self.limit_rub >= e:
            if d_dep+rub<self.limit_rub:
                dx=dx+st
            if d_dep+rub-self.limit_rub >= e:
                dx = dx-st/2.0
                st = st/2.0

            d_dep = d_deposit(dx)
            #print('ddep=',d_dep,'dx',dx)

        #print('Довнести',dx,'RUB')
        return dx







    #Вывод с Депозита
    def BTC_usd_OUT(self):

        '''Вывод через USD'''


        btc_pre = transf.presellBTC(self.btc,self.price_tosell_btcusd)
        usd = transf.sellBTC(btc_pre,self.price_tosell_btcusd,self.mk_tk_usd)['x'] #Получено при продаже

        usd_sum = usd+self.x_usd

        if (usd_sum < self.limit_usd):
            print('! меньше лимита', self.limit_usd)
            return

        u_out = depof.X_WITHD(usd_sum,self.u_out_dep_prc,self.u_out_dep_fix)  # На карте

        rub_u = exchf.sellUSD(u_out,self.usd_b)  #После перевода в USD на карте
        rub_u2 = exchf.sellUSD(u_out, self.old_usd_b)

        return{ 'btc':self.btc
               ,'btcsell':btc_pre
               ,'mk_tk':self.mk_tk_usd
               ,'usd_resed':self.x_usd
               ,'usd':usd
               ,'usd_sum':usd_sum
               ,'u_out':u_out
               ,'rub_u':rub_u
               ,'rub_u2':rub_u2
               }





    def BTC_rub_OUT(self):

        '''Вывод через USD'''

        #Вывод через USD
        btc_pre = transf.presellBTC(self.btc,self.price_tosell_btcrub)  # Предрасчет

        rub = transf.sellBTC(btc_pre, self.price_tosell_btcrub, self.mk_tk_rub)['x']
        rub_sum = rub + self.x_rub

        if (rub < self.limit_rub):
            print('! меньше лимита', self.limit_rub)

        rub_out = depof.X_WITHD(rub_sum, self.r_out_dep_prc, self.r_out_dep_fix)

        usd_r = exchf.buyUSD(rub_out,self.usd_s) #Переводим RUB в USD на карте
        usd_r2 = exchf.buyUSD(rub_out, self.old_usd_s)  # Переводим USD в рубли на карте

        return {'btc': self.btc
            , 'btcsell': btc_pre
            , 'mk_tk':self.mk_tk_rub
            , 'rub_resed':self.x_rub
            , 'rub': rub
            , 'rub_sum': rub_sum
            , 'rub_out':rub_out
            , 'usd_r': usd_r
            , 'usd_r2': usd_r2
                }





#=============XXXXX==================================

    #Вывод X с депозита
    #add USD дополнительный ввод USD на депозит, который тоже будет выводится вместе с суммой usd
    #add RUB дополнительный ввод RUB на депозит
    def X_OUT(self,type):

        #init
        x0 = 0
        add_x = 0
        add_x_dep = 0
        out_dep_pr = 1
        out_dep_fix = 0
        in_dep_pr = 1
        in_dep_fix = 0

        if(type=='USD'):
            x0 = self.x_usd
            add_x = self.add_usd

            out_dep_pr = self.u_out_dep_prc
            out_dep_fix = self.u_out_dep_fix
            in_dep_pr = self.u_in_dep_prc
            in_dep_fix = self.u_in_dep_fix

            exch_price = self.usd_b
            exch_price2 = self.old_usd_b

            def exch_curr(x,exch_price):
                return exchf.sellUSD(x,exch_price)

        if (type == 'RUB'):
            x0 = self.x_rub
            add_x = self.add_rub

            out_dep_pr = self.r_out_dep_prc
            out_dep_fix = self.r_out_dep_fix
            in_dep_pr = self.r_in_dep_prc
            in_dep_fix = self.r_in_dep_fix

            exch_price = self.usd_s
            exch_price2 = self.old_usd_s

            def exch_curr(x, exch_price):
                return exchf.buyUSD(x, exch_price)


        if(add_x>0):
            add_x_dep = depof.X_to_DEPO(add_x, in_dep_pr, in_dep_fix) #уйдет на депозит

        x = x0+add_x_dep
        x_out = depof.X_WITHD(x,out_dep_pr,out_dep_fix)  #X на карте

        x_curr = exch_curr(x_out,exch_price)    #Перевод X в Другую валюту
        x_curr2 = exch_curr(x_out,exch_price2)  #Перевод X в Другую валюту по другому курсу

        return{'x':x
               ,'add_usd':add_x            #сумма, добавленная на депозит
               ,'add_usd_dep':add_x_dep    #сумма надепозите
               ,'usd_out':x_out            #выедена с депозита
               ,'xcur':x_curr                #переведена в другую валюту
               ,'xcur2':x_curr2}             #по старому курсу


    #Вывод с Депозита
    def BTC_x_OUT(self,type):

        #init
        price_tosell_btc = 1
        mk_tk = 1
        x_lim = 0
        x0 = 0
        x_out_dep_prc = 1
        x_out_dep_fix = 0

        if(self.btc==0):
            print('На балансе 0 BTC')
            return {'btc':0}

        '''Вывод через USD'''
        if(type=='USD'):
            price_tosell_btc = self.price_tosell_btcusd
            mk_tk = self.mk_tk_usd
            x_lim = self.limit_usd
            x0 = self.x_usd
            x_out_dep_prc = self.u_out_dep_prc
            x_out_dep_fix = self.u_out_dep_fix
            exch_price = self.usd_b
            exch_price2 = self.old_usd_b

            def exch_curr(x, exch_price):
                return exchf.sellUSD(x, exch_price)

        '''Вывод через RUB'''
        if (type == 'RUB'):
            price_tosell_btc = self.price_tosell_btcrub
            mk_tk = self.mk_tk_rub
            x_lim = self.limit_rub
            x0 = self.x_rub
            x_out_dep_prc = self.r_out_dep_prc
            x_out_dep_fix = self.r_out_dep_fix
            exch_price = self.usd_s
            exch_price2 = self.old_usd_s

            def exch_curr(x, exch_price):
                return exchf.buyUSD(x, exch_price)



        btc_pre = transf.presellBTC(self.btc,price_tosell_btc)
        x = transf.sellBTC(btc_pre,price_tosell_btc,mk_tk)['x'] #Получено при продаже



        x_sum = x+x0

        if (x_sum < x_lim):
            print('! меньше лимита', x_lim)
            return

        x_out = depof.X_WITHD(x_sum,x_out_dep_prc,x_out_dep_fix)  # На карте

        x_cur = exch_curr(x_out,exch_price)  #После перевода в USD на карте
        x_cur2 = exch_curr(x_out,exch_price2)

        return{ 'btc':self.btc
               ,'btcsell':btc_pre
               ,'mk_tk':mk_tk
               ,'x_resed':x0
               ,'x':x                #сумма после продажи btc
               ,'x_sum':x_sum    #с учетом остатка на депозите
               ,'x_out':x_out    #вывелось на карту
               ,'x_cur':x_cur    #после перевода в другую валюту
               ,'x_cur2':x_cur2  #перевод в другую валюту по старому курсу
               }



    #Необходимо на депозите, чтобы на карту вывелось X0
    def X_on_DEPOSIT_to_OUT_X0(self, x_out, type='RUB'):


        if(type=='RUB'):
            percent = self.r_out_dep_prc
            fix = self.r_out_dep_fix
            comis = x_out * percent / 100 + fix
            x_on_depo = x_out + comis
            x_on_depo = cutX(x_on_depo + 0.01, 2)  # поправка. чтобы не высчитывать округление берется наибольшее число
            return x_on_depo


        elif(type=='USD'):
            percent = self.u_out_dep_prc
            fix = self.u_out_dep_fix
            comis = x_out * percent / 100 + fix
            x_on_depo = x_out + comis
            x_on_depo = cutX(x_on_depo + 0.01, 2)  # поправка. чтобы не высчитывать округление берется наибольшее число
            return x_on_depo

        else:
            print('Введен не верный тип. RUB либо USD')
            return None


    def BTC_on_DEPOSIT_to_GET_X0(self,x_exp,type):

        price = 1
        mk_tk = 1

        if(type=='RUB'):
            price = self.price_tosell_btcrub
            mk_tk = self.mk_tk_rub
        elif(type=='USD'):
            price = self.price_tosell_btcusd
            mk_tk = self.mk_tk_usd
        else:
            print('Введен не верный тип. RUB либо USD')

        btc0 = transf.sellBTCForX(x_exp, price, mk_tk)

        return {'btc':btc0,'price':price}

    def X_on_DEPOSIT_Y_out(self,X,price_tobuy,price_tosell,type_x='RUB',type_y='RUB'):
        '''
        :param X: Сумма ввода с карты
        :param price_tobuy: Цена покупки BTC
        :param price_tosell: Цена продажи BTC
        :param type_x: валюта ввода
        :param type_y: валюта вывода
        :return:
        '''
        dep_in_prc=1
        dep_in_fix = 0
        dep_out_prc = 1
        dep_out_fix = 0
        mk_tk = 0
        taker = 0

        if(type_x=='USD'):
            dep_in_prc = self.u_in_dep_prc
            dep_in_fix = self.u_in_dep_fix
            taker = self.taker
        elif(type_x=='RUB'):
            dep_in_prc = self.r_in_dep_prc
            dep_in_fix = self.r_in_dep_fix
            taker = self.taker



        if(type_y=='USD'):
            dep_out_prc = self.u_out_dep_prc
            dep_out_fix = self.u_out_dep_fix
            mk_tk = self.mk_tk_usd
        elif(type_y=='RUB'):
            dep_out_prc = self.r_out_dep_prc
            dep_out_fix = self.r_out_dep_fix
            mk_tk = self.mk_tk_usd




        x_depo = depof.X_to_DEPO(X, dep_in_prc, dep_in_fix)
        btc1 = transf.buyBTC(x_depo, price_tobuy, taker)['btc']


        y2 = transf.sellBTC(btc1,price_tosell,mk_tk)['x']
        y_out = depof.X_WITHD(y2,dep_out_prc,dep_out_fix)

        dp=None
        if(type_x==type_y):
            dp = price_tosell-price_tobuy

        return {'x_depo':x_depo
                ,'btc':btc1
                ,'y_depo':y2
                ,'y_out':y_out
                ,'dp':dp
                }

