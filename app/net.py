# net.py
# This file manages network connections.

import time
import threading
import json
import os
import hashlib

import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator


class zWorker():
    """
    ZMQ Networker. This class can be instantiated as a
    listener or a sender. Handles keeping the connection alive
    in a thread, and automatically polls/updates.
    """

    SENDER = 0
    LISTENER = 1

    def __init__(self, mode, datadir=None) -> None:
        self.mode = mode
        self.ctx = None
        self.data = None
        self.header = {}

        if datadir is None:
            self.datadir = os.path.dirname(__file__)
        else:
            self.datadir = datadir
        pass

    def start(self, port=None, host=None) -> bool:
        """
        Starts in whichever mode was selected.
        This involves setting claims to ports, managing keys and directories,
        and starting the main loops for each type of connection.
        """
        if self.mode == self.SENDER:
            # Server mode (REP)
            # needs to know the directory of certs

            if host is not None:
                print("why did you pass a host? im a server")
            root_dir = self.datadir
            keys_dir = os.path.join(root_dir, os.path.normpath('./data/server/'))
            public_keys_dir = os.path.join(root_dir, os.path.normpath('./data/friends/'))

            if not (
                os.path.exists(keys_dir)
                and os.path.exists(public_keys_dir)):
                print('Key directory missing')
                return False

            self.ctx = zmq.Context()
            self.auth = ThreadAuthenticator(self.ctx)

            self.auth.start()

            # this line must be rerun if a client key is added
            self.auth.configure_curve(domain='*', location=public_keys_dir)

            self.sock = self.ctx.socket(zmq.REP)

            server_secret_file = os.path.join(keys_dir, "server.key_secret")

            try:
                server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
            except:
                print('Unable to load server keys')
                return False

            self.sock.curve_secretkey = server_secret
            self.sock.curve_publickey = server_public
            self.sock.curve_server = True  # must come before bind
            
            self.sock.bind(f'tcp://*:{port}')
            print(f'bound to to tcp://*:{port}')
            
            self.t = threading.Thread(target=self.serverLoop,daemon=True)
            self.t.start()

        elif self.mode == self.LISTENER:
            print('starting listener')
            if host is None:
                print('listener needs a host')
                return False
            
            root_dir = self.datadir
            keys_dir = os.path.join(root_dir, os.path.normpath('./data/server/'))
            public_keys_dir = os.path.join(root_dir, os.path.normpath('./data/friends/'))

            if not (
                os.path.exists(keys_dir)
                and os.path.exists(public_keys_dir)):
                print('Key directory missing')
                return False

            try:
                fname = f"{host}.key"
                server_public_file = os.path.join(public_keys_dir, fname)
                print(server_public_file)
            except:
                print('Unable to load server pubkey')
                return False

            server_public, _ = zmq.auth.load_certificate(server_public_file)

            self.ctx = zmq.Context()
            self.sock = self.ctx.socket(zmq.REQ)

            client_secret_file = os.path.join(keys_dir, "server.key_secret")
            client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
            self.sock.curve_secretkey = client_secret
            self.sock.curve_publickey = client_public

            self.sock.curve_serverkey = server_public
            self.sock.connect(f'tcp://{host}:{port}')
            print(f'connecting to tcp://{host}:{port}')
            self.t = threading.Thread(target=self.clientLoop,daemon=True)
            self.t.start()
            print('done starting listener')
        else:
            return False
        
        return True

    def stop(self) -> bool:
        """
        Immediately terminate the connection.
        Theoretically, the connection could be started up again.
        This may make sense in cases wehre the server momentarily goes down
        and the client wants to reconnect. 
        """
        if self.sock is None:
            return False
        
        # FIXME currently not thread safe. 
        # https://github.com/starmaid/netkiss/issues/1
        self.ctx.destroy(linger=0)
        self.sock = None

        return True

    def getData(self) -> str:
        """Return stored data from the listener in JSON format"""
        if self.mode == self.LISTENER:
            return {'connected': True,
                    'type': self.header['type'],
                    'b64encoded': self.header['b64encoded'],
                    'data': self.data
                    }
        else:
            return None

    def setData(self, data, dtype, chain, encoded) -> bool:
        """Set data to be sent by the sender"""

        # TODO: Implement and check for a max file size
        # maybe do that on the web api side?

        if self.mode == self.SENDER:
            self.data = data
            self.header['id'] = hashlib.md5(self.data.encode()).hexdigest()
            self.header['time'] = time.time()
            self.header['chain'] = chain
            self.header['type'] = dtype
            self.header['b64encoded'] = encoded
            return True
        else:
            return False

    def serverLoop(self):
        """
        Loop to run forever for the server (sender).
        The server periodically refreshes what data is being served
        based on input from setData()
        """
        while self.sock is not None:
            print('serverloop start')
            try:
                message = self.sock.recv()
            except:
                print('server could not recieve msg')
                break
            print(f"Received request: {message}")
            
            try:
                req = json.loads(message)
            except json.JSONDecodeError:
                print('server could not decode json')
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
                    rep['body'] = self.data
            try:
                self.sock.send_string(json.dumps(rep))
            except:
                print('server could not send response')
                break
        return True
    
    # TODO: I dont know why I made these little methods.
    # Either find a use for them or get rid of them. 
    # I think they were to minimize traffic if a big file was
    # being sent. But I'm not using them.

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
        """
        Generically poll some data from the server
        """
        req = {}
        for f in fields:
            req[f] = True 
        try:
            self.sock.send_string(json.dumps(req))
        except:
            print('client could not send message')
            return None
        try:    
            message = self.sock.recv()
            try:
                rep = json.loads(message)
            except json.JSONDecodeError:
                print('client could not decode message')
                rep = None
        except:
            print('client could not recieve message')
            return None
        return rep

    def clientLoop(self):
        """
        Loop that runs forever as a client (Listener)
        Periodically updates the data availible in getData()
        """
        while self.sock is not None:
            print('in clientloop')
            rep = self.clientRequest(['ping','header','body'])
            if rep is not None:
                self.header = rep['header']
                self.data = rep['body']
                print(self.data)
            print('clientloop 5')

            # TODO: parameterize this sleep in the app config file
            time.sleep(5)

