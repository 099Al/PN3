# -*- coding: utf-8 -*-
'''
Элемент Tik  Содержит набор тиков, соответствующий заданной емкости
Имеет вид словаря {tid:,type:,unixdate:,amount:,price:}
'''


class TikQueue:

    def __init__(self, capasity):

        # Емкость должна быть переменной, чтобы входные данные не переполняли массив
        # Входные данные должны составлять процент от емкости
        self.capasity = capasity

        self.tikQ = []

        self.l_tid = []
        self.l_type = []
        self.l_unixdate = []
        self.l_amount = []
        self.l_price = []

    # набор tik-ов в аргументе подается по уменьшению слева на право  {101,100,99...}
    #Входной набор переворачивается
    def add_tail_revers_mode(self, tik):
        len_Que = len(self.tikQ)
        len_tik = len(tik)

        if len_tik >= self.capasity:  # Входящий набор больше емкости
            self.tikQ = tik[:self.capasity]  # заменяем все содержимое на последние(по времени/id элементи из входных данных
            self.tikQ = self.tikQ[::-1]  # разворот массива


        if len_tik < self.capasity:
            k = self.capasity - len_tik  # Количество элементов, которые необходимо оставить
            self.tikQ = self.tikQ[-k:]
            self.tikQ.extend(tik[::-1])  # Добавление новых элементов




    #В этом случае первый элемент массива это самый актуальный элемент
    def add_tail(self, tik):
        len_Que = len(self.tikQ)
        len_tik = len(tik)

        if len_tik >= self.capasity:  # Входящий набор больше емкости
            self.tikQ = tik[:self.capasity]  # заменяем все содержимое на последние(по времени/id элементи из входных данных
            # Без разворот массива

        if len_tik < self.capasity:
            k = self.capasity - len_tik  # Количество элементов, которые необходимо оставить
            self.tikQ = tik+self.tikQ[:k]  # Добавление новых элементов


    def remove_leading(self, k):
        self.tikQ = self.tikQ[k:]

    # Возвражяется список всех tid в очереди
    # если type = s, то только с типом s
    def get_list_tid(self, type='all'):
        if type == 'sell' or type == 's':
            return [x['tid'] for x in self.tikQ if x['type'] == 'sell']
        if type == 'buy' or type == 'b':
            return [x['tid'] for x in self.tikQ if x['type'] == 'buy']
        return [x['tid'] for x in self.tikQ]

    def get_list_type(self, type='all'):
        if type == 'sell' or type == 's':
            return [x['type'] for x in self.tikQ if x['type'] == 'sell']
        if type == 'buy' or type == 'b':
            return [x['type'] for x in self.tikQ if x['type'] == 'buy']
        return [x['type'] for x in self.tikQ]

    def get_list_unixdate(self, type='all'):
        if type == 'sell' or type == 's':
            return [x['date'] for x in self.tikQ if x['type'] == 'sell']
        if type == 'buy' or type == 'b':
            return [x['date'] for x in self.tikQ if x['type'] == 'buy']
        return [x['date'] for x in self.tikQ]

    def get_list_amount(self, type='all'):
        if type == 'sell' or type == 's':
            return [x['amount'] for x in self.tikQ if x['type'] == 'sell']
        if type == 'buy' or type == 'b':
            return [x['amount'] for x in self.tikQ if x['type'] == 'buy']
        return [x['amount'] for x in self.tikQ]

    def get_list_price(self, type='all'):
        if type == 'sell' or type == 's':
            return [x['price'] for x in self.tikQ if x['type'] == 'sell']
        if type == 'buy' or type == 'b':
            return [x['price'] for x in self.tikQ if x['type'] == 'buy']
        return [x['price'] for x in self.tikQ]



    #Поиск последних  n цен по заданному типу ордера
    def get_last_n_price_type(self,type,n):
        if (type == 'b'):
            type = 'buy'
        if (type == 's'):
            type = 'sell'


        p_list = []
        i=0
        for x in self.tikQ:
            if (x['type'] == type):
                p_list.append(x['price'])
                i=i+1
            if i >=n:
                return p_list

    #Поиск последних n цен по типу купить и продать
    def get_last_n_prices(self,n):

        p_sell_list = []
        p_buy_list = []
        s=0
        b=0
        for x in self.tikQ:


            if s>=n and b>=n:
                return {'buy':p_buy_list,'sell':p_sell_list}


            if (s<n and x['type'] == 'sell'):
                p_sell_list.append(x['price'])
                s=s+1

            if (b<n and x['type'] == 'buy'):
                p_buy_list.append(x['price'])
                b=b+1



    def get_last_n_prices_all(self, n):
        return [x['price'] for i,x in enumerate(self.tikQ) if i<n]



if __name__ == '__main__':
    pass