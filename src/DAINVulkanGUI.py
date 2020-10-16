#!/usr/bin/env python3

# Built-in modules
import os
import sys

# Local modules
import dain_ncnn_vulkan
import cain_ncnn_vulkan

# External modules
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


def error_popup(message):
    msg = QMessageBox()
    msg.setWindowTitle("Error")
    print(message)
    msg.setText(message)
    msg.exec_()


class Worker(QRunnable):
    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        print(self.kwargs)
        import DAINVulkanCLI
        DAINVulkanCLI.main(**self.kwargs)
        print("Done!")


class MainWindow(QMainWindow):
    def input_file_dialog_box(self):
        self.input_file = QFileDialog.getOpenFileName(None, 'Open input file', os.getenv('HOME'),
                                                      'Videos (*.mp4 *.mkv *.webm);;'
                                                      'Animated images (*.gif *.apng *.png);;'
                                                      'All Files (*)')[0]

        print("Selected input file: {}".format(self.input_file))
        if not self.input_file:
            self.input_label.setText('Input Path')
        else:
            self.input_label.setText(self.input_file)

    def output_file_dialog_box(self):
        self.output_dir = QFileDialog.getExistingDirectory(None, 'Choose output folder', os.getenv('HOME'))
        print("Selected output folder: {}".format(self.output_dir))
        if not self.output_dir:
            self.output_label.setText('Output Path')
        else:
            self.output_label.setText(self.output_dir)

    def interpolator_engine_combo_box_changed(self):
        print("combobox changed to", self.engine_combo_box.currentText())
        if self.engine_combo_box.currentText().lower().startswith("dain-ncnn"):
            self.tile_size_line_edit.setPlaceholderText(str(dain_ncnn_vulkan.DEFAULT_TILE_SIZE))
        elif self.engine_combo_box.currentText().lower().startswith("cain-ncnn"):
            self.tile_size_line_edit.setPlaceholderText(str(cain_ncnn_vulkan.DEFAULT_TILE_SIZE))

    def worker_execute(self):
        # Required arguments
        if not self.input_file:
            error_popup("Please specify an input file")
            raise ValueError("Input file not specified")
        if not self.output_dir:
            error_popup("Please specify an output folder")
            raise ValueError("Output folder not specified")

        kwargs = {
            "input_file": self.input_file,
            "output_folder": self.output_dir,
            "interpolator_engine": self.engine_combo_box.currentText(),
        }

        # Add optional arguments to kwargs only if specified
        if self.tile_size_line_edit.text():
            kwargs["tile_size"] = self.tile_size_line_edit.text()
        if self.gpu_id_line_edit.text():
            kwargs["gpu_id"] = self.gpu_id_line_edit.text()
        if self.threads_line_edit.text():
            kwargs["threads"] = self.threads_line_edit.text()

        # Execute
        worker = Worker(**kwargs)
        self.threadpool.start(worker)

    def __init__(self):
        super(MainWindow, self).__init__()

        # Create thread pool and limit to one thread
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        print("Multithreading with maximum {} threads".format(self.threadpool.maxThreadCount()))

        # Load layout from xml file
        uic.loadUi("gui_layout.ui", self)

        self.setWindowTitle("DAIN-Vulkan-GUI")

        # Input/Output
        self.input_file_button = self.findChild(QPushButton, 'inputFileButton')
        self.input_file_button.clicked.connect(self.input_file_dialog_box)
        self.input_file = None
        self.input_label = self.findChild(QLabel, 'inputFileLabel')

        self.output_file_button = self.findChild(QPushButton, 'outputFileButton')
        self.output_file_button.clicked.connect(self.output_file_dialog_box)
        self.output_dir = None
        self.output_label = self.findChild(QLabel, 'outputFileLabel')

        # Interpolator Engine Options
        self.engine_combo_box = self.findChild(QComboBox, "engineComboBox")
        self.engine_combo_box.currentTextChanged.connect(self.interpolator_engine_combo_box_changed)
        self.tile_size_line_edit = self.findChild(QLineEdit, 'tileSizeLineEdit')
        self.tile_size_line_edit.setPlaceholderText(str(dain_ncnn_vulkan.DEFAULT_TILE_SIZE))
        self.gpu_id_line_edit = self.findChild(QLineEdit, 'gpuIdLineEdit')
        self.gpu_id_line_edit.setPlaceholderText(dain_ncnn_vulkan.DEFAULT_GPU_ID)
        self.threads_line_edit = self.findChild(QLineEdit, 'threadsLineEdit')
        self.threads_line_edit.setPlaceholderText(dain_ncnn_vulkan.DEFAULT_THREADS)

        # Execute button
        self.execute_button = self.findChild(QPushButton, 'executeButton')
        self.execute_button.clicked.connect(self.worker_execute)

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
