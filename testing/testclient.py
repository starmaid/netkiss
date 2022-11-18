import sys
sys.path.append('..\\app')
from net import zWorker
import time
import os

def testname():
    print(__file__)

if __name__ == "__main__":
    s = zWorker(zWorker.LISTENER, datadir=os.path.dirname(__file__))
    started = s.start(port=6969,host='localhost')
    if started:
        print('started test client. trying to connect to localhost:6969')
        try:
            print(s.getData())
        except:
            s.stop()
            sys.exit()

        for i in range(30):
            print(i)
            time.sleep(1)
            
        print('stopping')
        s.stop()