import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit
from PyQt5.QtGui import QPainter, QColor, QBrush, QIcon

import socket
import time

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.addr = addr = ("192.168.0.222", 6454)

        self.initUI()


    def initUI(self):

        self.rows = 3
        self.cols = 3

        self.curState = []
        self.nextState = []

        for i in range(self.rows):
            t = []
            for j in range(self.cols):
                t.append(0)
            self.curState.append(t)

        self.setWindowTitle('Artnet tester')
        self.resize(400, 400)

        self.testCBox = QComboBox()
        self.testCBox.addItem(QIcon("img1.bmp"), "item1")
        self.testCBox.addItem(QIcon("img2.bmp"), "item2")

        self.btnSend = QPushButton("SEND")
        self.btnSend.clicked.connect(self.btnSend_clicked)

        self.btnSetAll = QPushButton("SET ALL")
        self.btnSetAll.clicked.connect(self.btnSetAll_clicked)

        self.listOfCBox = []

        self.setAllCBox = QComboBox()
        self.setAllCBox.addItems([str(i) for i in range(20)])

        for i in range(self.rows):
            tL = []
            for j in range(self.cols):
                cBox = QComboBox()
                cBox.addItems([str(i) for i in range(-1, 20)])
                cBox.setCurrentText("0")
                tL.append(cBox)
            self.listOfCBox.append(tL)


        self.timingText = QLineEdit()
        self.timingText.setText("1000")

        self.btnDropDown = QPushButton("DROP DOWN")
        self.btnDropDown.clicked.connect(self.animate_drop_down)
        self.btnConer = QPushButton("CONER")
        self.btnConer.clicked.connect(self.animate_coner)
        self.btnSnake = QPushButton("SNAKE")
        self.btnSnake.clicked.connect(self.animate_snake)
        self.hboxAnimate = QHBoxLayout()
        self.hboxAnimate.addWidget(self.timingText)
        self.hboxAnimate.addWidget(self.btnDropDown)




        self.hBoxL = QHBoxLayout()
        self.hBoxL.addWidget(self.setAllCBox)
        self.hBoxL.addWidget(self.btnSetAll)

        self.vBoxL = QVBoxLayout()

        self.gridL = QGridLayout()
        for i in range(self.rows):
            for j in range(self.cols):
                self.gridL.addWidget(self.listOfCBox[i][j], i, j)

        #self.vBoxL.addWidget(self.testCBox)
        self.vBoxL.addLayout(self.hBoxL)
        self.vBoxL.addLayout(self.gridL)
        self.vBoxL.addWidget(self.btnSend)
        self.vBoxL.addLayout(self.hboxAnimate)
        self.setLayout(self.vBoxL)
        self.show()

        self.sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def btnSend_clicked(self):
        l = []
        self.prep_data()
        self.curState = []

        for i in range(self.rows):
            t = []
            for j in range(self.cols):
                t.append(self.nextState[i][j])
            self.curState.append(t)

        l = self.serialize_cur_data()

        print(l)
        print(self.curState)
        print(self.nextState)
        #self.send_data(l)


    def btnSetAll_clicked(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.listOfCBox[i][j].currentText() != "-1":
                    self.listOfCBox[i][j].setCurrentText(self.setAllCBox.currentText())

    def prep_data(self):
        self.nextState = []
        t = []
        for i in range(self.rows):
            t = []
            for j in range(self.cols):
                t.append(int(self.listOfCBox[i][j].currentText()))
            self.nextState.append(t)

    def send_data(self, l):
        part1 = b'\x41\x72\x74\x2d\x4e\x65\x74\x00\x00\x50\x00\x0e'
        part2 = b'\x00\x00\x00\x00\x02\x00'
        part3 = bytes(l)
        data = part1 + part2 + part3
        self.sock.sendto(data, self.addr)

    def serialize_cur_data(self):
        l = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.curState[i][j] != -1:
                    l.append(self.curState[i][j])
        return l

    def animate_drop_down(self):
        delay = int(self.timingText.text())
        self.prep_data()
        print(self.nextState)
        print(self.curState)
        for i in range(self.rows):
            for j in range(self.cols):
                self.curState[i][j] = self.nextState[i][j]
            l = self.serialize_cur_data()
            print(l)
            time.sleep(delay/1000)

    def animate_slide_LR(self):
        pass

    def animate_slide_RL(self):
        pass

    def animate_snake(self):
        pass

    def animate_serial(self):
        pass

    def animate_corner(self):
        pass

    def animate_center(self):
        pass

    def closeEvent(self, event):
        # do stuff
        if self.sock:
            self.sock.close()  # let the window close


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())