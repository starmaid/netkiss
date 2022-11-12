import zmq
import time
import threading
import json

class zNetworking():

    SENDER = 0
    LISTENER = 1

    def __init__(self, mode) -> None:
        self.mode = mode
        self.ctx = None
        self.data = None
        self.header = None
        pass

    def start(self, port, host=None) -> bool:
        """starts in whichever mode was selected"""
        if self.mode == self.SENDER:
            if host is not None:
                print("why did you pass a host? im a server")
            
            self.ctx = zmq.Context()
            self.sock = self.ctx.socket(zmq.REP)
            self.sock.bind(f'tcp://*:{port}')
            
            self.t = threading.Thread(target=self.serverLoop)
            self.t.start()

        elif self.mode == self.LISTENER:
            
            if host is None:
                print('listener needs a host')
                return False

            self.ctx = zmq.Context()
            self.sock = self.ctx.socket(zmq.REQ)
            self.sock.connect(f'tcp://{host}:{port}')

            self.t = threading.Thread(target=self.clientLoop)
            self.t.start()

        else:
            return False
        
        return True

    def stop(self) -> bool:
        if self.sock is None:
            return False
        
        self.ctx.destroy(linger=0)
        self.sock = None

        return True

    def getData(self) -> str:
        if self.mode == self.LISTENER:
            return self.data
        else:
            return None

    def setData(self, data) -> bool:
        if self.mode == self.SENDER:
            self.data = data
            return True
        else:
            return False
    
    def getHeader(self) -> dict:
        if self.mode == self.LISTENER:
            return self.header
        else:
            return None

    def setHeader(self, header) -> bool:
        if self.mode == self.SENDER:
            self.header = header
            return True
        else:
            return False

    def serverLoop(self):
        while True:
            try:
                message = self.sock.recv()
            except:
                break
            print(f"Received request: {message}")
            
            try:
                req = json.loads(message)
            except json.JSONDecodeError:
                req = None

            rep = {}

            if req is None:
                rep['body'] = False
            else:
                if 'ping' in req.keys() and req['ping']:
                    rep['ping'] = time.time()
                if 'header' in req.keys() and req['header']:
                    rep['header'] = {}
                if 'body' in req.keys() and req['body']:
                    rep['body'] = None
            try:
                self.sock.send_string(f"response lol {time.monotonic()}")
            except:
                break
        return True
    
    def clientPing(self) -> float:
        rep = self.clientRequest(['ping'])
        return float(rep['ping'])

    def clientHeaders(self) -> dict:
        rep = self.clientRequest(['header'])
        return rep['header']

    def clientBody(self) -> dict:
        rep = self.clientRequest(['header','body'])
        return rep

    def clientRequest(self, fields=[]):
        req = {}
        for f in fields:
            req[f] = True 
        try:
            self.sock.send_string(json.dumps(req))
            message = self.sock.recv()
            try:
                rep = json.loads(message)
            except json.JSONDecodeError:
                rep = None
        except:
            return None
        return rep

    def clientLoop(self):
        while True:
            rep = self.clientBody()
            if rep is not None:
                self.header = rep['header']
                self.body = rep['body']
            time.sleep(5)

