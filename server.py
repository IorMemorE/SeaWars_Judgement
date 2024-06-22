import socket

class SeaWarServer:
    def __init__(self, port: int) -> None:
        self.server = socket.create_server(("127.0.0.1", port))
        self.conn: list[socket.socket] = []

    def deal(self):
        conn = self.conn[self.turn]
        other = self.conn[1 - self.turn]
        raw = conn.recv(64)
        msg, data = raw.split(b"\r\n")
        print(f"S{self.turn}:{msg},{data}")
        match msg:
            case b"Fail":
                data = data.decode()
                other.send(bytes(f"Win\r\n{self.turn}", "utf-8"))
                self.turn = 2
            case b"Attack":
                other.send(raw)
                self.turn = 1 - self.turn
            case b"Miss":
                other.send(raw)
            case b"Hitten":
                other.send(raw)
                self.turn = 1 - self.turn
            case _:
                pass

    # 拆线程运行
    def wait(self) -> bool:
        self.turn = 0
        while len(self.conn) != 2:
            conn, _ = self.server.accept()
            conn.recv(64)
            conn.send(bytes(f"Id\r\n{len(self.conn)}", "utf-8"))
            self.conn.append(conn)
            continue
        return len(self.conn) == 2

    def run(self):
        while self.turn < 2:
            # print(f"Running")
            self.deal()



