import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout,\
    QLabel, QGridLayout, QLineEdit
from PyQt5.QtGui import QPainter, QColor, QBrush, QIcon

import socket
import time

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.addr  = ("192.168.0.222", 6454)
        self.curTiming = 0
        self.initUI()


    def initUI(self):

        self.rows = 10
        self.cols = 25

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
        self.setAllCBox.addItems([str(i) for i in range(61)])

        self.btnTest = QPushButton("TEST")
        self.btnTest.clicked.connect(self.btnTest_clicked)

        for i in range(self.rows):
            tL = []
            for j in range(self.cols):
                cBox = QComboBox()
                cBox.addItems([str(i) for i in range(-1, 61)])
                cBox.setCurrentText("0")
                tL.append(cBox)
            self.listOfCBox.append(tL)


        self.timingText = QLineEdit()
        self.timingText.setText("1000")

        self.btnDropDown = QPushButton("DROP DOWN")
        self.btnDropDown.clicked.connect(self.animate_drop_down)
        self.btnCorner = QPushButton("CORNER")
        self.btnCorner.clicked.connect(self.animate_corner)
        self.btnSnake = QPushButton("SNAKE")
        self.btnSnake.clicked.connect(self.animate_snake)
        self.hboxAnimate = QHBoxLayout()
        self.hboxAnimate.addWidget(self.timingText)
        self.hboxAnimate.addWidget(self.btnDropDown)
        self.hboxAnimate.addWidget(self.btnCorner)
        self.hboxAnimate.addWidget(self.btnSnake)


        self.btnLR = QPushButton("LEFT RIGHT")
        self.btnLR.clicked.connect(self.animate_slide_LR)
        self.btnSerial = QPushButton("SERIAL")
        self.btnSerial.clicked.connect(self.animate_serial)
        self.btnCenter = QPushButton("CENTER")
        self.btnCenter.clicked.connect(self.animate_center)
        self.hboxAnimate2 = QHBoxLayout()
        self.hboxAnimate2.addWidget(self.btnLR)
        self.hboxAnimate2.addWidget(self.btnSerial)
        self.hboxAnimate2.addWidget(self.btnCenter)




        self.hBoxL = QHBoxLayout()
        self.hBoxL.addWidget(self.setAllCBox)
        self.hBoxL.addWidget(self.btnSetAll)

        self.vBoxL = QVBoxLayout()

        self.gridL = QGridLayout()
        for i in range(self.rows):
            for j in range(self.cols):
                self.gridL.addWidget(self.listOfCBox[i][j], i, j+1)

        for i in range(self.rows):
            self.gridL.addWidget(QLabel(str(i+1)), i, self.cols+1)
            self.gridL.addWidget(QLabel(str(i+1)), i, 0)

        for j in range(self.cols):
            self.gridL.addWidget(QLabel(str(j+1)), self.rows+1, j + 1)


        #self.vBoxL.addWidget(self.testCBox)
        self.vBoxL.addLayout(self.hBoxL)
        self.vBoxL.addLayout(self.gridL)
        self.vBoxL.addWidget(self.btnSend)
        self.vBoxL.addLayout(self.hboxAnimate)
        self.vBoxL.addLayout(self.hboxAnimate2)
        self.vBoxL.addWidget(self.btnTest)
        self.setLayout(self.vBoxL)
        self.show()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def btnTest_clicked(self):
        l = [5 for i in range(9)]

        self.send_data(l)

        time.sleep(4)

        l = [15 for i in range(9)]

        self.send_data(l)

        time.sleep(5)

        l = [0 for i in range(9)]

        self.send_data(l)

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
        self.send_data(l)


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
        if self.sock:
            self.sock.sendto(data, self.addr)
        print("data sent")

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
            self.send_data(l)
            print(l)
            time.sleep(delay/1000)

    def animate_slide_LR(self):
        delay = int(self.timingText.text())
        self.prep_data()
        print(self.nextState)
        print(self.curState)
        for col in range(self.cols):
            for row in range(self.rows):
                self.curState[row][col] = self.nextState[row][col]
            l = self.serialize_cur_data()
            self.send_data(l)
            print(l)
            time.sleep(delay / 1000)

    def animate_slide_RL(self):
        pass

    def animate_snake(self):
        delay = int(self.timingText.text())
        self.prep_data()
        print(self.nextState)
        print(self.curState)
        for row in range(self.rows):
            if row % 2 == 0:
                for col in range(self.cols-1, -1, -1):
                    self.curState[row][col] = self.nextState[row][col]
                    l = self.serialize_cur_data()
                    self.send_data(l)
                    print(l)
                    time.sleep(delay / 1000)
            else:
                for col in range(self.cols):
                    self.curState[row][col] = self.nextState[row][col]
                    l = self.serialize_cur_data()
                    self.send_data(l)
                    print(l)
                    time.sleep(delay / 1000)

    def animate_serial(self):
        delay = int(self.timingText.text())
        self.prep_data()
        print(self.nextState)
        print(self.curState)
        for row in range(self.rows):
            for col in range(self.cols):
                self.curState[row][col] = self.nextState[row][col]
                l = self.serialize_cur_data()
                self.send_data(l)
                print(l)
                time.sleep(delay / 1000)


    def animate_corner(self):
        delay = int(self.timingText.text())
        self.prep_data()
        print(self.nextState)
        print(self.curState)
        for row in range(self.rows):
            for row2 in range(row + 1):
                for col in range(row + 1):
                    self.curState[row2][col] = self.nextState[row2][col]
            l = self.serialize_cur_data()
            self.send_data(l)
            print(l)
            time.sleep(delay / 1000)

    def animate_center(self):
        pass

    def closeEvent(self, event):
        # do stuff
        if self.sock:
            self.sock.close()  # let the window close
            print("socket closed")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())