import zmq
import time
import threading
import json
import os
import hashlib

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
            # Server mode (REP)
            # needs to know the directory of certs

            if host is not None:
                print("why did you pass a host? im a server")
            
            #os.path.exists(keys_dir)

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

    def setData(self, data, dtype, chain, encoded) -> bool:
        if self.mode == self.SENDER:
            self.data = data
            self.header['id'] = hashlib.md5(self.body.encode()).hexdigest()
            self.header['time'] = time.time()
            self.header['chain'] = chain
            self.header['type'] = dtype
            self.header['b64encoded'] = encoded
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
                    rep['header'] = self.header
                if 'body' in req.keys() and req['body']:
                    rep['body'] = self.body
            try:
                self.sock.send_string(json.dumps(rep))
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
            rep = self.clientRequest(['ping','header','body'])
            if rep is not None:
                self.header = rep['header']
                self.body = rep['body']
            time.sleep(5)

