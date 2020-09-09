import os
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog


class Ui(QtWidgets.QMainWindow):

    def inputFileDialogBox(self):
        filename = QFileDialog.getOpenFileName(None, 'Open File', os.getenv('HOME'), 'Videos (*.mp4);; All Files (*)')
        print(filename[0])
        if not filename[0]:
            self.inputLabel.setText('Input Path.')
        else:
            self.inputLabel.setText(filename[0])

    def outputFileDialogBox(self):
        print(self.inputLabel.text())

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('GUI_Layout.ui', self)
        self.setWindowTitle('DAIN-Vulkan-GUI')
        self.inputFileButton = self.findChild(QtWidgets.QPushButton, 'inputFileButton')
        self.outputFileButton = self.findChild(QtWidgets.QPushButton, 'outputFileButton')
        self.inputLabel = self.findChild(QtWidgets.QLabel, 'inputFileLabel')

        self.inputFileButton.clicked.connect(self.inputFileDialogBox)
        self.outputFileButton.clicked.connect(self.outputFileDialogBox)
        self.show()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
