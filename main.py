import sys
from PySide6.QtWidgets import QApplication
from window import SeawarWindow 

def main():
    app = QApplication(sys.argv)
    sw = SeawarWindow(app)
    sw.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()