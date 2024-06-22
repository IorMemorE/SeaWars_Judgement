from concurrent.futures import ThreadPoolExecutor
import os
import signal
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtGui import QPaintEvent, QPainter, QPen, QColor, QColorConstants as Qc,QCloseEvent
from game import BoatsBuffer, SeaWar, standard_palce
from client import SeaWarClient
from server import SeaWarServer

from prepare import BoatListShower, BoatAdderBox, Connes, AttackControlor

class SeawarWindow(QMainWindow):
    def exit_me(self):
        os.kill(os.getpid(), signal.SIGTERM)

    def closeEvent(self, event:QCloseEvent):
        self.exit_me()

    def __init__(self, app: QCoreApplication) -> None:
        super().__init__()
        self.whoami = "Client"
        self.app = app
        self.bb = BoatsBuffer()
        # self.bb = standard_palce()
        self.tpe = ThreadPoolExecutor()
        self.init_ui()

    def init_ui(self):
        self.place = True
        self.setObjectName("MainWindow")
        self.setWindowTitle("海战联机")
        self.setFixedSize(1200, 500)
        self.add_boat_ui = BoatAdderBox(self, self.add_boat)
        self.boat_list_ui = BoatListShower(self)
        self.connes_ui = Connes(self)
        self.connes_ui.when_create(self.gcreate)
        self.connes_ui.when_join(self.gclient)

    def gcreate(self):
        self.whoami = "Server"
        try:
            self.bb.assume()
        except:
            qmsg = QMessageBox(self)
            qmsg.setWindowTitle("创建服务器失败")
            qmsg.setText("船只摆放未完成")
            qmsg.show()
            return

        cns: Connes = self.connes_ui
        try:
            port = cns.get_port()
            self.swserver = SeaWarServer(port)
            fu = self.tpe.submit(
                self.swserver.wait,
            )
        except:
            qmsg = QMessageBox(self)
            qmsg.setWindowTitle("创建服务器失败")
            qmsg.setText("端口错误")
            qmsg.show()
            return

        def gen_waiting_msg() -> QMessageBox:
            waiting = QMessageBox(self)
            waiting.setWindowTitle("等待加入")
            waiting.setText("等待加入")
            waiting.show()
            waiting.setStandardButtons(QMessageBox.StandardButton.NoButton)
            return waiting

        cns.ip_text.setText("127.0.0.1")
        self.gclient()

        waiting = gen_waiting_msg()
        while not fu.done():
            self.app.processEvents()
            if not waiting.isVisible():
                waiting = gen_waiting_msg()
        waiting.close()

        self.remake_ui()
        self.tpe.submit(
            self.swserver.run,
        )
        self.run()

    def gclient(self):
        try:
            self.sw = SeaWar(self.bb.assume())
        except:
            qmsg = QMessageBox(self)
            qmsg.setWindowTitle("加入游戏失败")
            qmsg.setText("船只摆放未完成")
            qmsg.show()
            return
        cns = self.connes_ui
        try:
            ip = cns.get_ip()
            port = cns.get_port()
            self.client = SeaWarClient(self.sw, ip, port)
        except:
            qmsg = QMessageBox(self)
            qmsg.setWindowTitle("加入游戏失败")
            qmsg.setText("无效的连接信息错误")
            qmsg.show()
            return
        if self.whoami != "Server":
            self.remake_ui()
            self.run()

    def remake_ui(self):
        self.place = False
        self.add_boat_ui.disapper()
        self.boat_list_ui.disapper()
        self.connes_ui.disapper()
        self.attack_control_ui = AttackControlor(self, self.attack)
        self.update()

    def run(self) -> None:
        self.tpe.submit(self.client.deal)
        while self.client.running:
            self.update()
            self.attack_control_ui.update(self.client.turn)
            self.app.processEvents()

        final = QMessageBox(self)
        final.setWindowTitle("游戏结束")
        if self.sw.alive():
            final.setText("你赢了")
        else:
            final.setText("你输了")
        final.show()
        final.buttonClicked.connect(self.exit_me)
        if not final.isVisible():
            self.exit_me()

    def attack(self):
        (acu := self.attack_control_ui)
        x = acu.get_x()
        y = acu.get_y()
        print(f"{self.whoami}: {x} {y}")
        if self.sw.oboard[x][y]:
            msg = QMessageBox(self)
            msg.setWindowTitle("参数错误")
            msg.setText("目标地点已经被摧毁")
            msg.show()
        else:
            self.client.send_attack(x, y)

    def add_boat(self):
        self.add_boat_ui.add_boat(self.bb)
        self.boat_list_ui.remake(self.bb)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        qp = QPainter()

        def draw_map(sx=40, sy=40, st=40, grid=10):
            qp.setPen(QPen(QColor(0, 0, 0), 3, Qt.PenStyle.SolidLine))
            for x in range(grid + 1):
                qp.drawLine(st * x + sx, sy, st * x + sx, sy + st * grid)
            for y in range(grid + 1):
                qp.drawLine(sx, st * y + sy, sx + st * grid, st * y + sy)

        def draw_single_boat(px: int, py: int, sx=40, sy=40, st=40):
            qp.drawEllipse(sy + (py - 1) * st, sx + (px - 1) * st, st, st)

        def draw_single_sink(px: int, py: int, sx=40, sy=40, st=40):
            qp.drawLine(
                sy + (py - 1) * st, sx + (px - 1) * st, sy + py * st, sx + px * st
            )
            qp.drawLine(
                sy + py * st, sx + (px - 1) * st, sy + (py - 1) * st, sx + px * st
            )

        def draw_placed_boats(sx=40, sy=40):
            qp.setPen(QPen(Qc.Blue, 2, Qt.PenStyle.DotLine))
            for boat in self.bb.arr:
                if boat.isv:
                    for row in range(boat.x, boat.x + boat.kind):
                        draw_single_boat(row, boat.y, sx, sy)
                else:
                    for col in range(boat.y, boat.y + boat.kind):
                        draw_single_boat(boat.x, col, sx, sy)

        def draw_sink(board: list[list[bool]], sx=40, sy=40, st=40, grid=10):
            qp.setPen(QPen(Qc.Red, 2, Qt.PenStyle.SolidLine))
            for i in range(1, 11):
                for j in range(1, 11):
                    if board[i][j]:
                        draw_single_sink(i, j, sx, sy, st)

        def draw_ohit(sx=500, sy=40, st=40, grid=10):
            qp.setPen(QPen(Qc.Green, 2, Qt.PenStyle.DotLine))
            for i in range(1, 11):
                for j in range(1, 11):
                    if self.sw.ohit[i][j]:
                        draw_single_boat(i, j, sy, sx, st)

        qp.begin(self)
        draw_map(40, 40)
        draw_placed_boats()
        if not self.place:
            draw_map(500, 40)
            draw_sink(self.sw.mboard, 40, 40)
            draw_sink(self.sw.oboard, 40, 500)
            draw_ohit(500, 40)
        qp.end()
