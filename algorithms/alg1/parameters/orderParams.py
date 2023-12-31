# -*- coding: utf-8 -*-

'''
Настроечные параметры для алгоритма
'''

# Процент от текущей цены

# Время ожидания

# Процент рисков


# Цена покупки
price_b = 5140
# Процент от баланса:
bx = 1

# Цена продажи
price_s = 5180

# Лимит
limit = 5130
limit_k1 = 0.01  # Процент от цены, последний покупки, чтобы установить лимит, ниже которого надо  продавать
limit_k2 = 0.02  ##Процент от цены, последний покупки, чтобы установить лимит, ниже которого надо  продавать

'''
p_buy>p(k1)>p(k2)
Вариант1: если цена меньше p(k1), то продаем по рынку
Вариант2: если цена меньше p(k1), то ставим ордер, но цена, чуть больше чем по рынку(чтобы был меньше процент)
                                            ордер меняется в зависимости от последней цены.
          если цена стала больше p(k1), то ордер снимается.
          если цена стала меньше p(k2), т.е. втоорая граница, то продать по рынку


'''






# Эту функцию надо удалить из всех модулей. Заменена на ProcessLine
class changeConstants():
    '''В дааном классе прставляются параметры для случая одного ордера
    Если необходимо будет делать несколько ордеров,
    то необходимо будет делать словарь из процессов
    В каждом процессе будет рассматриваться последовательность: купить-продать-сбросить.
    id должен записываться как порядковый номер, либо как номер id-ордера
    '''
    lastOrderFlag = ''  # Тип предыдущего ордера, который сработал (buy=b/sell=s)
    lastOrderType = 0  # Тип ордера. 0 - обычный. 1 - стоплосс типа 1

    lastBuyPrice = 0
    lastSellPrice = 0


    # стоп-ордер
    # т.е. необходимо быстро продавать.
    # либо еще какие-то действия. Тогда можно выставить другие значение.
    # 0 - начальное состояние. стоп не выставлен
    # 1 - выставляется стоп. Для первого лимита pa
    stopOrderFlag = 0  #!!!ВОЗМОЖНО НАДО УБРАТЬ ЭТОТ ПАРАМЕТР

    def set_lastOrderFlag(self, flag):
        changeConstants.lastOrderFlag = flag

    def set_lastOrderType(self,subtype):
        changeConstants.lastOrderType = subtype

    def set_lastBuyPrice(self, price):
        changeConstants.lastBuyPrice = price


    def set_lastSellPrice(self, price):
        changeConstants.lastSellPrice = price

    def set_stopOrderFlag(self, flag):
        changeConstants.stopOrderFlag = flag

    # рассчитывается лимит от последней lastBuyPrice
    def get_stopLimit_1(self):
        return self.lastBuyPrice * (1 - limit_k1)

    def get_stopLimit_2(self):
        return self.lastBuyPrice * (1 - limit_k2)


