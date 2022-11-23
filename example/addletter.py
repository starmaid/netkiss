import requests as r
import time
from random import randint

endpoint = 'http://localhost:80'

while True:
    d = r.get(f'{endpoint}/getdata')
    dobj = d.json()
    print(dobj)
    if 'data' in dobj and dobj['data'] is not None:
        dobj['data'] = ''.join([dobj['data'],chr(randint(65,80))])
    else:
        dobj['data'] = chr(randint(65,80))

    print(dobj)
    time.sleep(1)
    r.post(f'{endpoint}/setdata',data=dobj)
    for i in range(9):
        print(i)
        time.sleep(1)