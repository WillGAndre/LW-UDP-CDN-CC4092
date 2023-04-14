import uuid
import socket
import multiprocessing

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

class Listener:
    def __init__(self, port, buf_size, logger, addr=None) -> None:
        self.id = str(uuid.uuid4())[:9]
        if addr != None:
            self.addr = addr
        else:
            self.addr = get_ip()
        self.port = port
        self.buffer = buf_size
        self.logger = logger

    def handler(self, conn, addr):
        try:
            while True:
                data = conn.recv(self.buffer)
                if data == "":
                    self.logger.debug("socket closed")
                conn.sendall(data)
        except:
            self.logger.exception("Problem handling request")
        finally:
            self.logger.debug("Closing socket")
            conn.close()

    def listen(self):
        self.logger.debug(f"[{self.id}] Started bind @ {self.addr}:{self.port}")
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket.bind((self.addr, self.port))
        # self.socket.listen(1)

        # while True:
        #     conn, addr = self.socket.accept()

        