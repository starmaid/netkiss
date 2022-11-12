import zmq
import time
import threading


class zNetworking():

    SENDER = 0
    LISTENER = 1

    def __init__(self, mode) -> None:
        self.mode = mode
        self.ctx = None
        pass

    def start(self, port, host=None):
        """starts in whichever mode was selected"""
        if self.mode == self.SENDER:
            if host is not None:
                print("why did you pass a host? im a server")
            
            self.ctx = zmq.Context()
            self.sock = self.ctx.socket(zmq.REP)
            self.sock.bind(f'tcp://*:{port}')
            
            self.t = threading.Thread(target=self.serverLoop)
            self.t.start()

        elif self.mode == self.LISTNER:
            
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
        
        return

    def stop(self):
        if self.ctx is None:
            return False
        return

    def serverLoop(self):
        while True:
            try:
                message = self.sock.recv()
            except:
                break
            print(f"Received request: {message}")
            try:
                self.sock.send_string(f"response lol {time.monotonic()}")
            except:
                break

    def clientLoop(self):
        while True:
            try:
                print(f"Sending request...")
                self.sock.send_string("Hello")

                #  Get the reply.
                
                print('listening')
                message = self.sock.recv()
                print(f"Received reply [ {message} ]")
                time.sleep(1)
            except:
                break
