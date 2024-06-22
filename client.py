import socket
from game import SeaWar

class SeaWarClient:
    def send(self, msg: str):
        self.conn.send(bytes(msg, "utf-8"))

    def send_init(self):
        self.send(f"Init\r\n{self.sw.as_data()}")

    def send_attack(self, x: int, y: int):
        self.turn = False
        self.last_x = x
        self.last_y = y
        self.send(f"Attack\r\n{x} {y}")

    def send_suffer(self, x: int, y: int):
        if not self.sw.try_attack(x, y):
            self.send(f"Miss\r\n{self.sw.as_data()}")
            self.turn = True
            return
        if not self.sw.alive():
            self.running = False
            self.send(f"Fail\r\n{self.id}")
        else:
            self.send(f"Hitten\r\n{self.sw.as_data()}")
        self.turn = False

    def deal_once(self):
        if self.turn:
            return

        info, data = self.conn.recv(64).split(b"\r\n")
        print(f"Client-Get: {info} + {data}")
        match info:
            case b"Id":
                self.id = data.decode()
            case b"Attack":
                x, y = data.split(b" ")
                x = int(x)
                y = int(y)
                self.send_suffer(x, y)
            case b"Hitten":
                self.sw.success_hit(self.last_x, self.last_y)
                self.sw.update_from(data.decode())
                self.turn = True
            case b"Miss":
                self.turn = False
                self.sw.update_from(data.decode())
            case b"Win":
                self.running = False

    def deal(self):
        while self.running:
            self.deal_once()

    def __init__(self, sw: SeaWar, ip: str, port: int) -> None:
        self.sw: SeaWar = sw
        self.conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.conn.connect((ip, port))
        self.send_init()
        self.turn = False
        self.deal_once()
        if self.id == "0":
            self.turn = True
        self.running = True
