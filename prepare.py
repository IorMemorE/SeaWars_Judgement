from typing import Callable
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QVBoxLayout,
    QLineEdit,
)

from game import Boat, BoatsBuffer


class BoatAdderBox:
    def disapper(self):
        self.ui.setVisible(False)

    def __init__(self, parent, click, pos=(500, 450, 450, 50)) -> None:
        up = QWidget(parent)
        up.setObjectName("add_boat_detail")
        up.setGeometry(*pos)
        layout = QHBoxLayout(up)
        layout.setObjectName("add_boat_layout")
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.isv_box = QCheckBox(up)
        self.isv_box.setObjectName("isv_box")
        self.isv_box.setText("是否垂直")
        layout.addWidget(self.isv_box)

        self.kind_lab = QLabel(up)
        self.kind_lab.setObjectName("kind_lab")
        self.kind_lab.setText("长度:")
        self.kind_lab.setMaximumWidth(30)
        layout.addWidget(self.kind_lab)
        self.kind_box = QComboBox(up)
        for i in range(4):
            self.kind_box.addItem("")
            self.kind_box.setItemText(i, f"{i + 1}")
        self.kind_box.setObjectName("kind_box")
        layout.addWidget(self.kind_box)

        self.row_lab = QLabel(up)
        self.row_lab.setObjectName("row_lab")
        self.row_lab.setText("行:")
        self.row_lab.setMaximumWidth(20)
        layout.addWidget(self.row_lab)
        self.row_box = QComboBox(up)
        for i in range(10):
            self.row_box.addItem("")
            self.row_box.setItemText(i, f"{i + 1}")
        self.row_box.setObjectName("row_box")
        layout.addWidget(self.row_box)

        self.col_lab = QLabel(up)
        self.col_lab.setObjectName("row_lab")
        self.col_lab.setText("列:")
        self.col_lab.setMaximumWidth(20)
        layout.addWidget(self.col_lab)
        self.col_box = QComboBox(up)
        for i in range(10):
            self.col_box.addItem("")
            self.col_box.setItemText(i, f"{i + 1}")
        self.col_box.setObjectName("col_box")
        layout.addWidget(self.col_box)

        self.add_boat_btn = QPushButton(up)
        self.add_boat_btn.setObjectName("add_boat_btn")
        layout.addWidget(self.add_boat_btn)
        self.add_boat_btn.setText("添加")

        self.add_boat_btn.clicked.connect(click)
        self.ui = up

    def get_x(self) -> int:
        return self.row_box.currentIndex() + 1

    def get_y(self) -> int:
        return self.col_box.currentIndex() + 1

    def get_kind(self) -> int:
        return self.kind_box.currentIndex() + 1

    def get_isv(self) -> bool:
        return self.isv_box.isChecked()

    def add_boat(self, bb: BoatsBuffer):
        try:
            bb.add_boat(
                Boat(self.get_kind(), self.get_x(), self.get_y(), self.get_isv())
            )
            self.add_boat_btn.setText("添加")
        except:
            self.add_boat_btn.setText("添加失败，重试")


class BoatListShower:
    def __init__(self, pa: QWidget, pos=(500, 40, 450, 400)) -> None:
        self.pa = pa
        self.pos = pos
        self.ui = QWidget(self.pa)

    def disapper(self):
        self.ui.setVisible(False)

    def remove(self, bs: BoatsBuffer, id: int):
        bs.remove_boat(id)
        self.remake(bs)
        self.pa.update()

    def remake(self, bs: BoatsBuffer):
        self.ui.setVisible(False)
        self.ui = QWidget(self.pa)
        ui_lyt = QVBoxLayout(self.ui)
        for i, boat in enumerate(bs.arr):
            w = QWidget(self.ui)

            hlyt = QHBoxLayout()
            hlyt.setObjectName(f"bd{i}")

            qlab = QLabel(w)
            qlab.setText(
                f"船只{i}：\n{\
                f'长度:{boat.kind},行:{boat.x},列:{boat.y},{"垂直" if boat.isv else "水平"}'\
                }\n")
            hlyt.addWidget(qlab)

            qbtn = QPushButton(w)
            qbtn.setText("删除")
            qbtn.clicked.connect(lambda: self.remove(bs, i))
            hlyt.addWidget(qbtn)

            w.setLayout(hlyt)
            ui_lyt.addWidget(w)

        self.ui.setObjectName("boatlistShower")
        self.ui.setGeometry(*self.pos)
        self.ui.show()


class Connes:
    def __init__(self, pa, pos=(1000, 40, 200, 400)) -> None:
        ui = QWidget(pa)
        vlyt = QVBoxLayout(ui)

        def add_port_ui() -> QLineEdit:
            port_w = QWidget(ui)
            port_lyt = QHBoxLayout(port_w)
            port_lab = QLabel(port_w)
            port_lab.setText("端口:")
            port_text = QLineEdit(port_w)
            port_text.setText("51234")
            port_lyt.addWidget(port_lab)
            port_lyt.addWidget(port_text)
            vlyt.addWidget(port_w)
            return port_text

        def add_create_button() -> QPushButton:
            crt_btn = QPushButton(ui)
            crt_btn.setText("创建")
            vlyt.addWidget(crt_btn)
            return crt_btn

        def add_ip_ui() -> QLineEdit:
            ip_w = QWidget(ui)
            ip_lyt = QHBoxLayout(ip_w)
            ip_lab = QLabel(ip_w)
            ip_lab.setText("IP:")
            ip_text = QLineEdit(ip_w)
            ip_text.setText("127.0.0.1")
            ip_lyt.addWidget(ip_lab)
            ip_lyt.addWidget(ip_text)
            vlyt.addWidget(ip_w)
            return ip_text

        def add_join_button() -> QPushButton:
            join_btn = QPushButton(ui)
            join_btn.setText("加入")
            vlyt.addWidget(join_btn)
            return join_btn

        self.port_text = add_port_ui()
        self.create_btn = add_create_button()
        self.ip_text = add_ip_ui()
        self.join_btn = add_join_button()

        ui.setGeometry(*pos)
        self.ui = ui

    def when_create(self, fn: Callable):
        self.create_btn.clicked.connect(fn)

    def when_join(self, fn: Callable):
        self.join_btn.clicked.connect(fn)

    def get_ip(self) -> str:
        return self.ip_text.text()

    def get_port(self) -> int:
        p = int(self.port_text.text())
        assert 0 <= p and p <= 66535
        return p

    def disapper(self):
        self.ui.setVisible(False)


class AttackControlor:
    def __init__(self, parent, click, pos=(920, 40, 200, 200)) -> None:
        up = QWidget(parent)
        up.setObjectName("attact_ctrl")
        up.setGeometry(*pos)
        layout = QVBoxLayout(up)
        layout.setObjectName("attact_layout")
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.info_lab = QLabel(up)
        self.info_lab.setObjectName("info_lab")
        self.info_lab.setText("选择攻击目标")
        layout.addWidget(self.info_lab)

        self.row_lab = QLabel(up)
        self.row_lab.setObjectName("row_lab")
        self.row_lab.setText("行：")
        layout.addWidget(self.row_lab)
        self.row_box = QComboBox(up)
        for i in range(10):
            self.row_box.addItem("")
            self.row_box.setItemText(i, f"{i + 1}")
        self.row_box.setObjectName("row_box")
        layout.addWidget(self.row_box)

        self.col_lab = QLabel(up)
        self.col_lab.setObjectName("row_lab")
        self.col_lab.setText("列：")
        layout.addWidget(self.col_lab)
        self.col_box = QComboBox(up)
        for i in range(10):
            self.col_box.addItem("")
            self.col_box.setItemText(i, f"{i + 1}")
        self.col_box.setObjectName("col_box")
        layout.addWidget(self.col_box)

        self.attact_btn = QPushButton(up)
        self.attact_btn.setObjectName("attact_btn")
        layout.addWidget(self.attact_btn)
        self.attact_btn.setText("攻击！")

        self.attact_btn.clicked.connect(click)
        up.show()
        self.ui = up

    def get_x(self) -> int:
        return self.row_box.currentIndex() + 1

    def get_y(self) -> int:
        return self.col_box.currentIndex() + 1

    def update(self, o: bool):
        self.attact_btn.setVisible(o)
