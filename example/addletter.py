import requests as r
import time
from random import randint

endpoint = 'http://localhost:80'

while True:
    d = r.get(f'{endpoint}/getdata')
    print(d.json())
    d['data'] = ''.join([d['data'],chr(randint(65,80))])
    time.sleep(1)
    r.post(f'{endpoint}/setdata',data=d.json())
    for i in range(9):
        print(i)
        time.sleep(1)