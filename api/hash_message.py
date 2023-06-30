# -*- coding: utf-8 -*-
# Не разработан
# Кодировка в SHA

import hmac
import hashlib


import datetime
from datetime import datetime
import tzlocal


nonce = 1
customer_id = 123456
API_SECRET = 'thekey'
api_key = 'thapikey'


message = '{} {} {}'.format(nonce, customer_id, api_key)

signature = hmac.new(bytes(API_SECRET , 'latin-1'), msg = bytes(message , 'latin-1'), digestmod = hashlib.sha256).hexdigest().upper()
print(signature)



if __name__ == '__main__':
    print(1)
    dt = datetime.datetime.now()
    print(dt)

