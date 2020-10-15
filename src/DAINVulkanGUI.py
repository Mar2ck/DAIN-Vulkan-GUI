#!/usr/bin/env python3

# Built-in modules
import os
import sys

# Local modules
import dain_ncnn_vulkan
# import cain_ncnn_vulkan

# External modules
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Worker(QRunnable):
    @pyqtSlot()
    def run(self):
        import time
        print("Start test worker")
        time.sleep(5)


class MainWindow(QMainWindow):

    def input_file_dialog_box(self):
        input_file = QFileDialog.getOpenFileName(None, 'Open input file', os.getenv('HOME'),
                                                 'Videos (*.mp4 *.mkv *.webm);;'
                                                 'Animated images (*.gif *.apng *.png);;'
                                                 'All Files (*)')
        # input_file = output if output is not None else input_file

        print(input_file[0])
        if not input_file[0]:
            self.input_label.setText('Input Path')
        else:
            self.input_label.setText(input_file[0])

    def output_file_dialog_box(self):
        output_dir = QFileDialog.getExistingDirectory(None, 'Choose output folder', os.getenv('HOME'))
        print(output_dir)
        if not output_dir:
            self.output_label.setText('Output Path')
        else:
            self.output_label.setText(output_dir)

    def worker_execute(self):
        print("Tilesize: ", self.tile_size_line_edit.text())
        worker = Worker()
        self.threadpool.start(worker)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        uic.loadUi('gui_layout.ui', self)
        self.setWindowTitle('DAIN-Vulkan-GUI')

        # Input/Output
        self.input_file_button = self.findChild(QPushButton, 'inputFileButton')
        self.input_file_button.clicked.connect(self.input_file_dialog_box)
        self.input_label = self.findChild(QLabel, 'inputFileLabel')
        self.output_file_button = self.findChild(QPushButton, 'outputFileButton')
        self.output_file_button.clicked.connect(self.output_file_dialog_box)
        self.output_label = self.findChild(QLabel, 'outputFileLabel')

        # Interpolator Engine Options
        self.tile_size_line_edit = self.findChild(QLineEdit, 'tileSizeLineEdit')
        self.tile_size_line_edit.setPlaceholderText(str(dain_ncnn_vulkan.DEFAULT_TILE_SIZE))
        # TODO add function for changing tile-size placeholder text based on engineComboBox
        self.gpu_id_line_edit = self.findChild(QLineEdit, 'gpuIdLineEdit')
        self.gpu_id_line_edit.setPlaceholderText(dain_ncnn_vulkan.DEFAULT_GPU_ID)
        self.threads_line_edit = self.findChild(QLineEdit, 'threadsLineEdit')
        self.threads_line_edit.setPlaceholderText(dain_ncnn_vulkan.DEFAULT_THREADS)

        self.execute_button = self.findChild(QPushButton, 'executeButton')
        self.execute_button.clicked.connect(self.worker_execute)

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
