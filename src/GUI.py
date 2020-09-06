import GUI_Layout
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    form = GUI_Layout.Ui_MainWindow()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()