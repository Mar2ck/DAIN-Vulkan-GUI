import os
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog


class Ui(QtWidgets.QMainWindow):

    def input_file_dialog_box(self):
        input_file = QFileDialog.getOpenFileName(None, 'Open File', os.getenv('HOME'), 'Videos (*.mp4; *.mkv; *.webm; '
                                                                                       '*gif);; All Files (*)')
        if not input_file[0]:
            self.input_label.setText('Input Path.')
        else:
            self.input_label.setText(input_file[0])

    def output_file_dialog_box(self):
        output_dir = QFileDialog.getSaveFileName(None, 'Save File', os.getenv('HOME'), 'Videos (*.mp4; *.mkv; *.webm; '
                                                                                       '*gif);; All Files (*)')
        if not output_dir[0]:
            self.output_label.setText('Output Path.')
        else:
            self.output_label.setText(output_dir[0])

    def ffmpeg_parse(self):
        print(self.input_label.text())

        # FfmpegExtractFrames(self.inputLabel[0], self.outputLabel[0])

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('GUI_Layout.ui', self)
        self.setWindowTitle('DAIN-Vulkan-GUI')

        # Buttons and fields we can change
        self.input_file_button = self.findChild(QtWidgets.QPushButton, 'inputFileButton')
        self.output_file_button = self.findChild(QtWidgets.QPushButton, 'outputFileButton')
        self.ffmpeg_button = self.findChild(QtWidgets.QPushButton, 'ffmpeg')
        self.input_label = self.findChild(QtWidgets.QLabel, 'inputFileLabel')
        self.output_label = self.findChild(QtWidgets.QLabel, 'outputFileLabel')

        # This is the on click commands
        self.input_file_button.clicked.connect(self.input_file_dialog_box)
        self.output_file_button.clicked.connect(self.output_file_dialog_box)
        self.ffmpeg_button.clicked.connect(self.ffmpeg_parse)
        self.show()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
