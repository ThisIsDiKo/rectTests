import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout,\
    QLabel, QGridLayout, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

import configparser
import copy
import socket
import time
from random import shuffle

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        try:
            with open("stylesTest.css", "r") as fh:
                self.setStyleSheet(fh.read())
        except:
            pass

        self.btnFirstStep = QPushButton("1\n(1 -> 18)")
        self.btnSecondStep = QPushButton("2\n(1 -> 0)")
        self.btnThirdStep = QPushButton("3\n(511 -> 18)")
        self.btnFourthStep = QPushButton("4\n(511 -> 0)")

        self.btnFirstStep.clicked.connect(self.first_clicked)
        self.btnSecondStep.clicked.connect(self.second_clicked)
        self.btnThirdStep.clicked.connect(self.third_clicked)
        self.btnFourthStep.clicked.connect(self.fourth_clicked)

        self.grid = QGridLayout()
        self.grid.addWidget(self.btnFirstStep, 0, 0)
        self.grid.addWidget(self.btnSecondStep, 0, 1)
        self.grid.addWidget(self.btnThirdStep, 1, 0)
        self.grid.addWidget(self.btnFourthStep, 1, 1)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socketAddr = ("192.168.0.222", 6454)

        self.setLayout(self.grid)
        self.setWindowTitle("Тестировщик")
        self.show()

    def first_clicked(self):
        l = [0 for i in range(511)]
        l[0] = 18
        self.send_data(l)

    def second_clicked(self):
        l = [0 for i in range(511)]
        self.send_data(l)

    def third_clicked(self):
        l = [0 for i in range(511)]
        l[510] = 18
        self.send_data(l)

    def fourth_clicked(self):
        l = [0 for i in range(511)]
        self.send_data(l)

    def send_data(self, l):
        part1 = b'\x41\x72\x74\x2d\x4e\x65\x74\x00\x00\x50\x00\x0e' #первая часть преамбулы
        part2 = b'\x00\x00\x00\x00\x02\x00' #вторая часть преамбулы
        part3 = bytes(l)    #Массив данных, для отправки на календари (последовательность байт с позициями)
        data = part1 + part2 + part3
        if self.sock:
            self.sock.sendto(data, self.socketAddr)
        print("data sent", l)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ControlPanel()
    sys.exit(app.exec_())
