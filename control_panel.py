import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout,\
    QLabel, QGridLayout, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt

import configparser
import copy
import socket
import time
from random import shuffle

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        config = configparser.ConfigParser()
        try:
            config.read('config.cfg')
            self.rows = int(config.get("Settings", "rows"))
            self.cols = int(config.get("Settings", "cols"))
            ip = config.get("Settings", "ip")
            port = int(config.get("Settings", "port"))
            self.socketAddr = (ip, port)
        except:
            print("no config file")
            self.rows = 10
            self.cols = 25
            self.socketAddr = ("192.168.0.222", 6454)

        try:
            with open("styles.css", "r") as fh:
                self.setStyleSheet(fh.read())
        except:
            pass

        self.sock = None
        self.curSlide = []
        self.nessSlide = []

        self.mainLayout = QVBoxLayout()
        self.gridL = QGridLayout()

        self.init_head()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.setLayout(self.mainLayout)
        self.setWindowTitle("Панель управления календарями")
        self.show()

    def init_head(self):
        self.lblNetSettings = QLabel("Настройки подключения")
        self.lblIpSettings = QLabel("IP адрес")
        self.txtIpSettings = QLineEdit(self.socketAddr[0])
        self.lblPortSettings = QLabel("Порт")
        self.txtPortSettings = QLineEdit(str(self.socketAddr[1]))

        self.lblMatrixSettings = QLabel("Параметры матрицы")
        self.txtRowSettings = QLineEdit(str(self.rows))
        self.txtColSettings = QLineEdit(str(self.cols))
        self.btnUseSettings = QPushButton("Применить")
        self.btnUseSettings.clicked.connect(self.btnUseSettings_clicked)


        hboxNet = QHBoxLayout()
        hboxNet.addWidget(QLabel("Настройки подключения"))
        hboxNet.addWidget(QLabel("IP адрес"))
        hboxNet.addWidget(self.txtIpSettings)
        hboxNet.addWidget(QLabel("Порт"))
        hboxNet.addWidget(self.txtPortSettings)

        hboxMatrix = QHBoxLayout()
        hboxMatrix.addWidget(QLabel("Параметры матрицы"))
        hboxMatrix.addWidget(self.txtRowSettings)
        hboxMatrix.addWidget(QLabel("x"))
        hboxMatrix.addWidget(self.txtColSettings)
        hboxMatrix.addWidget(self.btnUseSettings)

        self.mainLayout.addLayout(hboxNet)
        self.mainLayout.addLayout(hboxMatrix)
        #self.mainLayout.addLayout(self.gridL)

    def init_matrix(self):
        self.cBoxNessSlide = QComboBox()
        self.cBoxNessSlide.setMaxVisibleItems(20)
        self.cBoxNessSlide.addItems([str(i) for i in range(0, 20)])
        self.btnSetAll = QPushButton('Установить все')
        self.btnSetAll.clicked.connect(self.btnSetAll_clicked)
        self.btnSetAll.setObjectName("SetAll")

        self.listOfCBox = []
        for i in range(self.rows):
            tL = []
            for j in range(self.cols):
                cBox = QComboBox()
                cBox.addItems([str(i) for i in range(0, 20)])
                cBox.setCurrentText("0")
                cBox.setMaxVisibleItems(20)
                tL.append(cBox)
            self.listOfCBox.append(tL)

        self.gridL = QGridLayout()
        self.curSlide = []
        for i in range(self.rows):
            t = []
            for j in range(self.cols):
                t.append(0)
                self.gridL.addWidget(self.listOfCBox[i][j], i, j + 1)
            self.curSlide.append(t)

        for i in range(self.rows):
            self.gridL.addWidget(QLabel(str(i + 1)), i, self.cols + 1)
            self.gridL.addWidget(QLabel(str(i + 1)), i, 0)

        for j in range(self.cols):
            self.gridL.addWidget(QLabel(str(j + 1)), self.rows + 1, j + 1)

        self.btnSend = QPushButton('Отправить')
        self.btnSend.setFixedHeight(40)
        self.btnSend.setFixedWidth(200)
        self.btnSend.clicked.connect(self.btnSend_clicked)
        self.btnSend.setObjectName("Send")

        hboxSetAll = QHBoxLayout()
        hboxSetAll.addWidget(QLabel("Слайд"))
        hboxSetAll.addWidget(self.cBoxNessSlide)
        hboxSetAll.addWidget(self.btnSetAll)

        self.mainLayout.addLayout(hboxSetAll)
        self.mainLayout.addLayout(self.gridL)
        self.mainLayout.addWidget(self.btnSend, alignment=Qt.AlignCenter)
        self.btnUseSettings.setDisabled(True)

    def init_animations(self):
        self.txtAnimationStep = QLineEdit("500")
        self.cBoxAnimationType = QComboBox()
        self.cBoxAnimationType.addItems(['none', 'waterfall', 'wave', 'snake', 'serial', 'check',
                                         'noise', 'arrow', 'conner'])
        self.cBoxAnimationDirection = QComboBox()
        self.cBoxAnimationDirection.addItems(['up down', 'down up', 'left right', 'right left',
                                              'left top', 'right top',
                                              'left bottom', 'right bottom', 'center'])
        self.btnGenerate = QPushButton('Сгенерированить')
        self.btnGenerate.setFixedHeight(40)
        self.btnGenerate.setFixedWidth(200)
        self.btnGenerate.clicked.connect(self.btnGenerate_clicked)
        self.btnGenerate.setObjectName("Generate")

        hboxAnimation = QHBoxLayout()
        hboxAnimation.addWidget(QLabel('Шаг анимации (мс)'))
        hboxAnimation.addWidget(self.txtAnimationStep)
        hboxAnimation.addWidget(QLabel('Тип'))
        hboxAnimation.addWidget(self.cBoxAnimationType)
        hboxAnimation.addWidget(QLabel('Направление'))
        hboxAnimation.addWidget(self.cBoxAnimationDirection)
        #hboxAnimation.addWidget(self.btnGenerate)

        t = QLabel("АНИМАЦИЯ")
        t.setAlignment(Qt.AlignCenter)
        t.setObjectName("AnimLbl")
        self.mainLayout.addWidget(t)
        self.mainLayout.addLayout(hboxAnimation)
        self.mainLayout.addWidget(self.btnGenerate, alignment=Qt.AlignCenter)

    def btnSetAll_clicked(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.listOfCBox[i][j].currentText() != "-1":
                    self.listOfCBox[i][j].setCurrentText(self.cBoxNessSlide.currentText())

    def btnSend_clicked(self):
        data = self.prep_data()
        self.curSlide = copy.deepcopy(data[:])
        for i in self.curSlide:
            print(i)
        data = self.serialize_cur_data(data)
        self.send_data(data)

    def btnGenerate_clicked(self):
        data = self.prep_data()
        self.nessSlide = copy.deepcopy(data[:])
        animStepTime = 50
        animType = self.cBoxAnimationType.currentText()
        animDir = self.cBoxAnimationDirection.currentText()
        try:
            animStepTime = int(self.txtAnimationStep.text())
        except:
            self.show_error_dialog("Неправильное время шага анимации")

        animationTypeDir = {'none': self.animation_idle,
                            'waterfall': self.animation_waterfall,
                            'wave': self.animation_wave,
                            'snake': self.animation_snake,
                            'serial': self.animation_serial,
                            'check': self.animation_check,
                            'noise': self.animation_noise,
                            'arrow': self.animation_arrow,
                            'conner': self.animation_conner}

        print("btn generate clicked")
        animationArea = self.find_animation_area()
        animationTypeDir[animType](animStepTime, animDir, animationArea)

    def btnUseSettings_clicked(self):
        try:
            port = int(self.txtPortSettings.text())
            ip = self.txtIpSettings.text()
            self.socketAddr = (ip, port)
        except Exception as e:
            self.show_error_dialog("Неправильные данные сети")
            return

        try:
            self.rows = int(self.txtRowSettings.text())
            self.cols = int(self.txtColSettings.text())
        except Exception as e:
            #print(e.message)
            self.show_error_dialog("Неправильные данные матрицы")
            return

        config = configparser.ConfigParser()
        config.add_section('Settings')
        config.set("Settings", "rows", str(self.rows))
        config.set("Settings", "cols", str(self.cols))
        config.set("Settings", "ip", ip)
        config.set("Settings", "port", str(port))
        with open('config.cfg', 'w') as configFile:
            config.write(configFile)

        self.init_matrix()
        self.init_animations()

    def send_data(self, l):
        part1 = b'\x41\x72\x74\x2d\x4e\x65\x74\x00\x00\x50\x00\x0e'
        part2 = b'\x00\x00\x00\x00\x02\x00'
        part3 = bytes(l)
        data = part1 + part2 + part3
        if self.sock:
            self.sock.sendto(data, self.socketAddr)
        print("data sent")

    def serialize_cur_data(self, l):
        t = []
        for i in range(self.rows):
            for j in range(self.cols):
                if l[i][j] != -1:
                    t.append(l[i][j])
        return t

    def prep_data(self):
        slideInfo = []
        for i in range(self.rows):
            t = []
            for j in range(self.cols):
                t.append(int(self.listOfCBox[i][j].currentText()))
            slideInfo.append(t)
        return slideInfo

    def animation_waterfall(self, delay, direction, animationArea):
        startRow, startCol, endRow, endCol = animationArea
        if direction == "up down":
            for row in range(startRow, endRow + 1):
                for col in range(startCol, endCol + 1):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                self.send_step(delay)
        elif direction == "down up":
            for row in range(endRow, startRow - 1, - 1):
                for col in range(startCol, endCol + 1):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                self.send_step(delay)
        elif direction == "left right":
            for col in range(startCol, endCol + 1):
                for row in range(startRow, endRow + 1):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                self.send_step(delay)
        elif direction == "right left":
            for col in range(endCol, startCol - 1, -1):
                for row in range(startRow, endRow + 1):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                self.send_step(delay)
        else:
            self.show_error_dialog("Неправильно выбрано направление для анимации")

    def animation_wave(self, delay, direction, animationArea):
        startRow, startCol, endRow, endCol = animationArea
        if direction == "left top":
            for col in range(startCol, endCol + (endRow - startRow) + 1):
                for col1 in range(startCol, col + 1):
                    for row1 in range(startRow, startRow + col - col1 + 1):
                        if (startRow <= row1 <= endRow) and (startCol <= col1 <= endCol):
                            self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                self.send_step(delay)
        elif direction == "right top":
            for col in range(endCol, startCol - (endRow - startRow) - 1, -1):
                for col1 in range(endCol, col - 1, -1):
                    for row1 in range(startRow, startRow + col1 - col + 1):
                        if (startRow <= row1 <= endRow) and (startCol <= col1 <= endCol):
                            self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                self.send_step(delay)
        elif direction == "left bottom":
            for col in range(startCol, endCol + (endRow - startRow) + 1):
                for col1 in range(startCol, col + 1):
                    for row1 in range(endRow, endRow - col + col1 - 1, -1):
                        if (startRow <= row1 <= endRow) and (startCol <= col1 <= endCol):
                            self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                self.send_step(delay)
        elif direction == "right bottom":
            for col in range(endCol, startCol - (endRow - startRow) - 1, -1):
                for col1 in range(endCol, col - 1, -1):
                    for row1 in range(endRow, endRow - col1 + col - 1, -1):
                        if (startRow <= row1 <= endRow) and (startCol <= col1 <= endCol):
                            self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                self.send_step(delay)
        elif direction == "center":
            if (endRow - startRow + 1) % 2 != 0:
                r1 = startRow + int((endRow - startRow) / 2)
                r2 = startRow + int((endRow - startRow) / 2)
            else:
                r1 = startRow +int((endRow - startRow) / 2)
                r2 = r1 + 1

            if (endCol - startCol + 1) % 2 != 0:
                c1 = startCol + int((endCol - startCol) / 2)
                c2 = startCol + int((endCol - startCol) / 2)
            else:
                c1 = startCol + int((endCol - startCol) / 2)
                c2 = c1 + 1

            if (endRow - startRow) > (endCol - startCol):
                st = int((endRow - startRow) / 2)
            else:
                st = int((endCol - startCol) / 2)

            for step in range(st+1):
                for col in range(c1-step, c2+step+1):
                    for row in range(r1-step, r2+step+1):
                        if (row <= endRow and row >= startRow) and (col <= endCol and col >= startCol):
                            self.curSlide[row][col] = self.nessSlide[row][col]
                self.send_step(delay)
        else:
            self.show_error_dialog("Неправильно выбрано направление для анимации")

    def animation_snake(self, delay, direction, animationArea):
        startRow, startCol, endRow, endCol = animationArea
        if direction == "left top":
            side = True
            for row in range(startRow, endRow + 1):
                if side:
                    for col in range(startCol, endCol + 1):
                        self.curSlide[row][col] = self.nessSlide[row][col]
                        self.send_step(delay)
                    side = False
                else:
                    for col in range(endCol, startCol - 1, -1):
                        self.curSlide[row][col] = self.nessSlide[row][col]
                        self.send_step(delay)
                    side = True
        elif direction == "right top":
            side = False
            for row in range(startRow, endRow + 1):
                if side:
                    for col in range(startCol, endCol + 1):
                        self.curSlide[row][col] = self.nessSlide[row][col]
                        self.send_step(delay)
                    side = False
                else:
                    for col in range(endCol, startCol - 1, -1):
                        self.curSlide[row][col] = self.nessSlide[row][col]
                        self.send_step(delay)
                    side = True
        elif direction == "left bottom":
            side = True
            for row in range(endRow, startRow-1,  -1):
                if side:
                    for col in range(startCol, endCol + 1):
                        self.curSlide[row][col] = self.nessSlide[row][col]
                        self.send_step(delay)
                    side = False
                else:
                    for col in range(endCol, startCol - 1, -1):
                        self.curSlide[row][col] = self.nessSlide[row][col]
                        self.send_step(delay)
                    side = True
        elif direction == "right bottom":
            side = False
            for row in range(endRow, startRow - 1, -1):
                if side:
                    for col in range(startCol, endCol + 1):
                        self.curSlide[row][col] = self.nessSlide[row][col]
                        self.send_step(delay)
                    side = False
                else:
                    for col in range(endCol, startCol - 1, -1):
                        self.curSlide[row][col] = self.nessSlide[row][col]
                        self.send_step(delay)
                    side = True
        else:
            self.show_error_dialog("Неправильно выбрано направление для анимации")

    def animation_serial(self, delay, direction, animationArea):
        startRow, startCol, endRow, endCol = animationArea
        if direction == "left top":
            for row in range(startRow, endRow + 1):
                for col in range(startCol, endCol + 1):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                    self.send_step(delay)
        elif direction == "right top":
            for row in range(startRow, endRow + 1):
                for col in range(endCol, startCol - 1, -1):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                    self.send_step(delay)
        elif direction == "left bottom":
            for row in range(endRow, startRow - 1, -1):
                for col in range(startCol, endCol + 1):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                    self.send_step(delay)
        elif direction == "right bottom":
            for row in range(endRow, startRow - 1, -1):
                for col in range(endCol, startCol - 1, -1):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                    self.send_step(delay)
        else:
            self.show_error_dialog("Неправильно выбрано направление для анимации")


    def animation_noise(self, delay, direction, animationArea):
        startRow, startCol, endRow, endCol = animationArea
        NUMBER_OF_POINTS = 5
        listOfImg = []
        for row in range(startRow, endRow + 1):
            for col in range(startCol, endCol + 1):
                pos = (row, col)
                listOfImg.append(pos[:])

        shuffle(listOfImg)
        sizeOfList = len(listOfImg)

        for step in range(0, sizeOfList, NUMBER_OF_POINTS):
            for subStep in range(NUMBER_OF_POINTS):
                if listOfImg:
                    pos = listOfImg.pop()
                    self.curSlide[pos[0]][pos[1]] = self.nessSlide[pos[0]][pos[1]]
            self.send_step(delay)

    def animation_check(self, delay, direction, animationArea):
        startRow, startCol, endRow, endCol = animationArea

        side = True
        for row in range(startRow, endRow + 1):
            if side:
                for col in range(startCol, endCol + 1, 2):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                side = False
            else:
                for col in range(startCol + 1, endCol + 1, 2):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                side = True

        self.send_step(delay)

        side = False
        for row in range(startRow, endRow + 1):
            if side:
                for col in range(startCol, endCol + 1, 2):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                side = False
            else:
                for col in range(startCol + 1, endCol + 1, 2):
                    self.curSlide[row][col] = self.nessSlide[row][col]
                side = True

        self.send_step(delay)

    def animation_arrow(self, delay, direction, animationArea):
        startRow, startCol, endRow, endCol = animationArea
        if (endRow - startRow + 1) % 2 != 0:
            r1 = startRow + int((endRow - startRow) / 2)
            r2 = startRow + int((endRow - startRow) / 2)
        else:
            r1 = startRow + int((endRow - startRow) / 2)
            r2 = r1 + 1

        if direction == 'left right':
            for step in range(startCol, endCol + int((r1 + r2) / 2) + 1):
                for col in range(startCol, step + 1):
                    for row in range(step - col + 1):
                        if (startRow <= (r1 - row) <= endRow) and (startCol <= col <= endCol):
                            self.curSlide[r1 - row][col] = self.nessSlide[r1 - row][col]
                        if (startRow <= (r2 + row) <= endRow) and (startCol <= col <= endCol):
                            self.curSlide[r2 + row][col] = self.nessSlide[r2 + row][col]
                self.send_step(delay)
        elif direction == 'right left':
            for step in range(startCol, endCol + int((r1 + r2) / 2) + 1):
                for col in range(endCol, endCol - step - 1, -1):
                    for row in range(col - (endCol - step) + 1):
                        if (startRow <= (r1 - row) <= endRow) and (startCol <= col <= endCol):
                            self.curSlide[r1 - row][col] = self.nessSlide[r1 - row][col]
                        if (startRow <= (r2 + row) <= endRow) and (startCol <= col <= endCol):
                            self.curSlide[r2 + row][col] = self.nessSlide[r2 + row][col]
                self.send_step(delay)
        else:
            self.show_error_dialog("Неправильно выбрано направление для анимации")

    def animation_conner(self, delay, direction, animationArea):
        startRow, startCol, endRow, endCol = animationArea

        if direction == "left top":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
            else:
                mostDirection = True

            if mostDirection:
                for col in range(startCol, endCol + 1):
                    for col1 in range(startCol, col + 1):
                        for row1 in range(startRow, startRow + col - startCol + 1):
                            if row1 <= endRow and row1 >= startRow:
                                self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                    self.send_step(delay)
            else:
                for row in range(startRow, endRow + 1):
                    for row1 in range(startRow, row + 1):
                        for col1 in range(startCol, startCol + (row - startRow) + 1):
                            if col1 <= endCol and col1 >= startCol:
                                self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                    self.send_step(delay)

        elif direction == "right top":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
            else:
                mostDirection = True
            if mostDirection:
                for col in range(endCol, startCol - 1, -1):
                    for col1 in range(endCol, col - 1, -1):
                        for row1 in range(startRow, startRow + (endCol - col) + 1):
                            if row1 <= endRow and row1 >= startRow:
                                self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                    self.send_step(delay)
            else:
                for row in range(startRow, endRow + 1):
                    for row1 in range(startRow, row + 1):
                        for col1 in range(endCol, endCol - (row - startRow) - 1, -1):
                            if col1 <= endCol and col1 >= startCol:
                                self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                    self.send_step(delay)

        elif direction == "left bottom":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
            else:
                mostDirection = True

            if mostDirection:
                for col in range(startCol, endCol + 1):
                    for col1 in range(startCol, col + 1):
                        for row1 in range(endRow, endRow - (col - startCol) - 1, -1):
                            if row1 <= endRow and row1 >= startRow:
                                self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                    self.send_step(delay)
            else:
                for row in range(endRow, startRow - 1, -1):
                    for row1 in range(endRow, row - 1, -1):
                        for col1 in range(startCol, startCol + (endRow - row) + 1):
                            if col1 <= endCol and col1 >= startCol:
                                self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                    self.send_step(delay)
        elif direction == "right bottom":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
            else:
                mostDirection = True

            if mostDirection:
                for col in range(endCol, startCol - 1, -1):
                    for col1 in range(endCol, col - 1, -1):
                        for row1 in range(endRow, endRow - (endCol - col) - 1, -1):
                            if row1 <= endRow and row1 >= startRow:
                                self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                    self.send_step(delay)
            else:
                for row in range(endRow, startRow - 1, -1):
                    for row1 in range(endRow, row - 1, -1):
                        for col1 in range(endCol, endCol - (endRow - row) - 1, -1):
                            if col1 <= endCol and col1 >= startCol:
                                self.curSlide[row1][col1] = self.nessSlide[row1][col1]
                    self.send_step(delay)
        elif direction == "center":
            if (endRow - startRow + 1) % 2 != 0:
                r1 = startRow + int((endRow - startRow) / 2)
                r2 = startRow + int((endRow - startRow) / 2)
            else:
                r1 = startRow + int((endRow - startRow) / 2)
                r2 = r1 + 1

            if (endCol - startCol + 1) % 2 != 0:
                c1 = startCol + int((endCol - startCol) / 2)
                c2 = startCol + int((endCol - startCol) / 2)
            else:
                c1 = startCol + int((endCol - startCol) / 2)
                c2 = c1 + 1

            if (endRow - startRow) > (endCol - startCol):
                st = int((endRow - startRow) / 2)
            else:
                st = int((endCol - startCol) / 2)

            for step in range(st + 1):
                for col in range(c1 - step, c2 + step + 1):
                    for row in range(r1 - step, r2 + step + 1):
                        if (row <= endRow and row >= startRow) and (col <= endCol and col >= startCol):
                            self.curSlide[row][col] = self.nessSlide[row][col]
                self.send_step(delay)
        else:
            self.show_error_dialog("Неправильно выбрано направление для анимации")

    def animation_idle(self, *k):
        l = self.prep_data()

        for i in l:
            print(i)

        l = self.serialize_cur_data(l)
        self.send_data(l)

    def send_step(self, delay):
        for i in self.curSlide:
            print(i)

        l = self.serialize_cur_data(self.curSlide)
        self.send_data(l)
        time.sleep(delay / 1000)

    def find_animation_area(self,):
        maxRow = 0
        maxCol = 0
        minRow = len(self.curSlide)
        minCol = len(self.curSlide[0])

        for row in range(self.rows):
            for col in range(self.cols):
                if self.curSlide[row][col] != self.nessSlide[row][col]:
                    if row > maxRow:
                        maxRow = row
                    if row < minRow:
                        minRow = row
                    if col > maxCol:
                        maxCol = col
                    if col < minCol:
                        minCol = col

        return(minRow, minCol, maxRow, maxCol)

    def show_error_dialog(self, s):
        message = QMessageBox()
        message.setIcon(QMessageBox.Critical)
        message.setText(s)
        message.exec_()

    def closeEvent(self, event):
        # do stuff
        #self.closeEvent(event)
        if self.sock:
            self.sock.close()  # let the window close
        print("socket closed")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ControlPanel()
    sys.exit(app.exec_())
