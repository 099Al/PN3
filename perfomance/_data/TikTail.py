# -*- coding: utf-8 -*-
'''
Элемент Tik  Содержит набор тиков, соответствующий заданной емкости
Имеет вид словаря {tid:,type:,unixdate:,amount:,price:}
capacity - минимальная длина списка.
один из мписков должен быть не меньше заданной длины capacity.
втрой список может быть больше из-за не равномерного распределения типов тиков.
разрывов по времени внутри списка быть недолжно.
'''

class TikTail:

    def __init__(self,capacity):

        self.capacity = capacity

        self.sell_tail =[]  #список ордеров, которые сработали на покупку
        self.buy_tail = []
        self.queue = []   # общая емкость

        self.sell_prices = []
        self.buy_prices = []


    def add_tail(self,new_data):

        new_sell = []
        new_buy = []
        new_queue = []

        new_sell_prices = []
        new_buy_prices = []


        for x in new_data:
            if(len(new_sell)<self.capacity or len(new_buy)<self.capacity):
                if (x['type']=='sell'):
                    new_sell.append(x)
                    new_sell_prices.append(x['price'])
                else:                       #if (x['type'=='buy'])
                    new_buy.append(x)
                    new_buy_prices.append(x['price'])
                new_queue.append(x)
            else:
                break

        #цикл завершен, но список мог не заполниться

        dl_sell = self.capacity - len(new_sell)
        dl_buy = self.capacity - len(new_buy)


        dl = max(dl_buy,dl_sell)

        if(dl>0):  #список не заполнился
            tik_0 = None
            if (dl_sell==dl):  #т.е. не заполнился sell
                d_list_s = self.sell_tail[:dl]          #добавление недостающих элементов по sell
                self.sell_tail = new_sell+d_list_s
                self.sell_prices = new_sell_prices + self.sell_prices[:dl]

                d_list_b = []
                pos = 0
                if(len(d_list_s)>0):                    #добавление недостающих элементов по buy
                    tik_0 = d_list_s[-1]['tid']                #Id - tik последего элемента в списке, чтобы примерн до этого времени отобрать tik-и по buy
                    pos = self.__positionTik__(tik_0,self.buy_tail)
                    d_list_b = self.buy_tail[:pos]
                self.buy_tail = new_buy+d_list_b
                self.buy_prices = new_buy_prices + self.buy_prices[:pos]
            else:
                d_list_b = self.buy_tail[:dl]
                self.buy_tail = new_buy + d_list_b
                self.buy_prices = new_buy_prices + self.buy_prices[:dl]

                pos = 0
                d_list_s = []
                if(len(d_list_b)>0):
                    tik_0 = d_list_b[-1]['tid']
                    pos = self.__positionTik__(tik_0, self.sell_tail)
                    d_list_s = self.sell_tail[:pos]
                self.sell_tail = new_sell + d_list_s
                self.sell_prices = new_sell_prices + self.sell_prices[:pos]

            d_list_q=[]
            if(tik_0!=None):
                pos_q = self.__positionTik__(tik_0,self.queue)
                d_list_q = self.queue[:pos_q]
            self.queue = new_queue+d_list_q


        else:  # все заполнилось
            self.sell_tail = new_sell
            self.sell_prices = new_sell_prices

            self.buy_tail = new_buy
            self.buy_prices = new_buy_prices

            self.queue = new_queue





    def __positionTik__(self,tik,list):
        for i,el in enumerate(list):
            if (el['tid']<tik):
                return i

        return len(list)





    def get_sell(self):
        return self.sell_tail

    def get_buy(self):
        return self.buy_tail

    def get_queue(self):
        return self.queue

    def last_tiks(self):
        return{ 'buy':self.buy_tail
                ,'sell':self.sell_tail
                ,'queue':self.queue}



    def last_prices(self):
        return {'buy':self.buy_prices
                ,'sell':self.sell_prices
                }






