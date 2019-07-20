import json
import copy
from random import shuffle
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy, QLineEdit, QComboBox, QPushButton,
                             QHBoxLayout, QVBoxLayout, QWidget)
import time
class ProcessJSON(QWidget):
    def __init__(self):
        super(ProcessJSON, self).__init__()

        self.scenario = Scenario()


        self.open_file()

        #self.scenario.check_timecodes()
        #self.scenario.prepare_animation()

    def open_file(self):
        print("Open file")
        fileName, _ = QFileDialog.getOpenFileName(self, "Открыть файл", QDir.currentPath())
        print(fileName)
        if fileName:
            data = None
            with open(fileName, 'r') as readFile:
                data = json.load(readFile)

            start_time = time.time()
            self.scenario.init_slides(data)
            print("--- %s seconds ---" % (time.time() - start_time))
            print("data read")

class Slide:
    def __init__(self):
        self.id = 0
        self.timecode = 0
        self.images = []
        self.animation = {}


class Scenario:
    def __init__(self):
        self.slides = []
        self.width = 25
        self.height = 10

        self.callType = 'Simple'

        self.animationTypeDict = {"0": 'None',
                                  "1": 'waterfall',
                                  "2": 'wave',
                                  "3": 'snake',
                                  "4": 'serial',
                                  "5": 'noise',
                                  "6": 'check',
                                  "7": 'arrow',
                                  "8": 'conner'}

        self.animationDirDict = {'0': 'up_down',
                                 '1': 'down_up',
                                 '2': 'left_right',
                                 '3': 'right_left',
                                 '4': 'lt_conner',
                                 '5': 'rt_conner',
                                 '6': 'lb_conner',
                                 '7': 'rb_conner',
                                 '8': 'center'}

        self.animationFuncDict = {'None': self.idle_animation,
                                  'waterfall': self.waterfall_animation,
                                  'wave': self.wave_animation,
                                  'snake': self.snake_animation,
                                  'serial': self.serial_animation,
                                  'noise': self.noise_animation,
                                  'check': self.check_animation,
                                  'arrow': self.arrow_animation,
                                  'conner': self.conner_animation
                                  }


    def check_time_code(self):
        prevTimecode = 0
        if not self.slides:
            return "Список слайдов пуст"
        for slide in self.slides:
            if slide.timecode >= prevTimecode:
                prevTimecode = slide.timecode
            else:
                return "Некорректное время начала слайда {}".format(self.slides.index(slide)+1)
        return "Время начала слайдов корректно"

    def init_slides(self, s):
        preSlides = s

        for data in preSlides:
            slide = Slide()
            #Копируем Id
            slide.id = int(data['id'])

            #Преобразование времени
            prepMs = data['timecode'].split(':')
            minutes = int(prepMs[0])
            seconds = int(prepMs[1])
            milliseconds = int(prepMs[2])
            slide.timecode = minutes * 60 * 1000 + seconds * 1000 + milliseconds

            #Преобразование одномерного массива в двумерный и перевод в числовые значения
            slide.images = []
            t = []
            counter = 0
            for img in data['images']:
                t.append(int(img) - 1)
                counter += 1
                if counter == self.width:
                    counter = 0
                    slide.images.append(t)
                    t = []

            # Преобразование анимации
            animType = self.animationTypeDict[data['animation'][0]['type']]

            try:
                animTime = int(data['animation'][0]['time'])
                if animTime < 40:
                    animTime = 40
            except:
                animTime = None

            try:
                animRounds = int(data['animation'][0]['rpm'])
                if animRounds > 10:
                    animRounds = 10

                for row in range(len(slide.images)):
                    for col in range(len(slide.images[0])):
                        slide.images[row][col] = 20 * animRounds + slide.images[row][col]
            except:
                animRounds = None

            try:
                animDirection = data['animation'][0]['direction']
                animDirection = self.animationDirDict[data['animation'][0]['direction']]
            except:
                animDirection = None

            animation = {}
            animation['type'] = animType
            animation['stepTime'] = animTime
            animation['rounds'] = animRounds
            animation['direction'] = animDirection

            slide.animation = animation.copy()

            self.slides.append(slide)

        for slide in self.slides:
            self.print_debug('slide {} animation: {}'.format(slide.id, slide.animation))

        print(self.check_time_code())
        self.process_animations()

    def process_animations(self):
        simpleData = []
        for slideNum in range(len(self.slides)):
            data = self.animationFuncDict[self.slides[slideNum].animation['type']](self.slides[slideNum-1],
                                                                                   self.slides[slideNum])
            if self.callType == 'Full':
                #print(data)
                pass
            else:
                msTime = data['endTime']
                minuteTime = int(msTime / 60000)
                secondTime = int((msTime - minuteTime*60000) / 1000)
                msTime = msTime % 1000
                data['endTime'] = "{}:{}:{}".format(minuteTime, secondTime, msTime)
                simpleData.append(data)

        if self.callType == 'Full':
            # print(data)
            pass
        else:
            json_data = json.dumps(simpleData)
            self.print_response_animation_time(json_data)

    def idle_animation(self, prevSlide, slide):
        if self.callType == 'Full':
            strSegment = ""
            strSegment += self.prepare_serial_data(slide.timecode, slide.images)

            strDebug = "+++\n+++ SLIDE ID {}\n+++\n".format(slide.id)
            strDebug += "------------------------------------------\n"
            strDebug += "timing: {}\n".format(slide.timecode)
            for row in slide.images:
                strDebug += "{}\n".format(row)
            strDebug += "------------------------------------------\n"
            self.print_debug(strDebug)

            return strSegment
        else:
            data = dict()
            data["id"] = slide.id
            data["endTime"] = slide.timecode

            self.print_debug(data)

            return data

    def waterfall_animation(self, prevSlide, slide):
        startRow, startCol, endRow, endCol = self.find_animation_area(prevSlide, slide)
        time = slide.timecode
        direction = slide.animation['direction']
        timeStep = slide.animation['stepTime']
        stepsList = []
        stepDict = {}
        stepArray = prevSlide.images[:]
        nessSlide = slide.images[:]
        maxMovement = 0

        if direction == "up_down":
            for row in range(startRow, endRow + 1):
                for col in range(startCol, endCol + 1):
                    movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                    if movement > maxMovement:
                        maxMovement = movement
                    if self.callType == 'Full':
                        stepArray[row][col] = nessSlide[row][col]

                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))

        elif direction == "down_up":
            for row in range(endRow, startRow-1, - 1):
                for col in range(startCol, endCol + 1):
                    movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                    if movement > maxMovement:
                        maxMovement = movement
                    if self.callType == 'Full':
                        stepArray[row][col] = nessSlide[row][col]

                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))
        elif direction == "left_right":
            for col in range(startCol, endCol + 1):
                for row in range(startRow, endRow + 1):
                    movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                    if movement > maxMovement:
                        maxMovement = movement
                    if self.callType == 'Full':
                        stepArray[row][col] = nessSlide[row][col]

                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))

        elif direction == "right_left":
            for col in range(endCol, startCol - 1, -1):
                for row in range(startRow, endRow + 1):
                    movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                    if movement > maxMovement:
                        maxMovement = movement
                    if self.callType == 'Full':
                        stepArray[row][col] = nessSlide[row][col]

                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))

        if self.callType == 'Full':
            strSegment = ""
            for step in stepsList:
                strSegment += self.prepare_serial_data(step['time'], step['images'])

            strDebug = "+++\n+++ SLIDE ID {}\n+++\n".format(slide.id)
            strDebug += "------------------------------------------\n"
            for step in stepsList:
                strDebug += "timing: {}\n".format(step['time'])
                for row in step['images']:
                    strDebug += "{}\n".format(row)
                strDebug += "------------------------------------------\n"
            self.print_debug(strDebug)

            return strSegment
        else:
            data = dict()
            data["id"] = slide.id
            data["endTime"] = slide.timecode + maxMovement * 200 + len(stepsList) * timeStep

            self.print_debug(data)

            return data

    def wave_animation(self, prevSlide, slide):
        startRow, startCol, endRow, endCol = self.find_animation_area(prevSlide, slide)
        time = slide.timecode
        direction = slide.animation['direction']
        timeStep = slide.animation['stepTime']
        stepsList = []
        stepDict = {}
        stepArray = prevSlide.images[:]
        nessSlide = slide.images[:]
        maxMovement = 0

        if direction == "lt_conner":
            for col in range(startCol, endCol + (endRow - startRow) + 1):
                for col1 in range(startCol, col + 1):
                    for row1 in range(startRow, startRow + col - col1 + 1):
                        if (startRow <= row1 <= endRow) and (startCol <= col1 <= endCol):
                            movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[row1][col1] = nessSlide[row1][col1]
                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))
        elif direction == "rt_conner":
            for col in range(endCol, startCol - (endRow - startRow) - 1, -1):
                for col1 in range(endCol, col - 1, -1):
                    for row1 in range(startRow, startRow + col1 - col + 1):
                        if (startRow <= row1 <= endRow) and (startCol <= col1 <= endCol):
                            movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[row1][col1] = nessSlide[row1][col1]
                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))
        elif direction == "lb_conner":
            for col in range(startCol, endCol + (endRow - startRow) + 1):
                for col1 in range(startCol, col + 1):
                    for row1 in range(endRow, endRow - col + col1 - 1, -1):
                        if (startRow <= row1 <= endRow) and (startCol <= col1 <= endCol):
                            movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[row1][col1] = nessSlide[row1][col1]
                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))
        elif direction == "rb_conner":
            for col in range(endCol, startCol - (endRow - startRow) - 1, -1):
                for col1 in range(endCol, col - 1, -1):
                    for row1 in range(endRow, endRow - col1 + col - 1, -1):
                        if (startRow <= row1 <= endRow) and (startCol <= col1 <= endCol):
                            movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[row1][col1] = nessSlide[row1][col1]
                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))
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
                            movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[row][col] = nessSlide[row][col]
                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))

        if self.callType == 'Full':
            strSegment = ""
            for step in stepsList:
                strSegment += self.prepare_serial_data(step['time'], step['images'])

            strDebug = "+++\n+++ SLIDE ID {}\n+++\n".format(slide.id)
            strDebug += "------------------------------------------\n"
            for step in stepsList:
                strDebug += "timing: {}\n".format(step['time'])
                for row in step['images']:
                    strDebug += "{}\n".format(row)
                strDebug += "------------------------------------------\n"
            self.print_debug(strDebug)

            return strSegment
        else:
            data = dict()
            data["id"] = slide.id
            data["endTime"] = slide.timecode + maxMovement * 200 + len(stepsList) * timeStep

            self.print_debug(data)

            return data

    def snake_animation(self, prevSlide, slide):
        startRow, startCol, endRow, endCol = self.find_animation_area(prevSlide, slide)
        time = slide.timecode
        direction = slide.animation['direction']
        timeStep = slide.animation['stepTime']
        stepsList = []
        stepDict = {}
        stepArray = prevSlide.images[:]
        nessSlide = slide.images[:]
        maxMovement = 0

        if direction == "lt_conner":
            side = True
            for row in range(startRow, endRow+1):
                if side:
                    for col in range(startCol, endCol+1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray
                            stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray
                            stepsList.append(copy.deepcopy(stepDict))
                    side = True
        if direction == "rt_conner":
            side = False
            for row in range(startRow, endRow+1):
                if side:
                    for col in range(startCol, endCol+1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray
                            stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray
                            stepsList.append(copy.deepcopy(stepDict))
                    side = True
        if direction == "lb_conner":
            side = True
            for row in range(endRow, startRow-1,  -1):
                if side:
                    for col in range(startCol, endCol+1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray
                            stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray
                            stepsList.append(copy.deepcopy(stepDict))
                    side = True
        if direction == "rb_conner":
            side = False
            for row in range(endRow, startRow-1,  -1):
                if side:
                    for col in range(startCol, endCol+1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray
                            stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray
                            stepsList.append(copy.deepcopy(stepDict))
                    side = True

        if self.callType == 'Full':
            strSegment = ""
            for step in stepsList:
                strSegment += self.prepare_serial_data(step['time'], step['images'])

            strDebug = "+++\n+++ SLIDE ID {}\n+++\n".format(slide.id)
            strDebug += "------------------------------------------\n"
            for step in stepsList:
                strDebug += "timing: {}\n".format(step['time'])
                for row in step['images']:
                    strDebug += "{}\n".format(row)
                strDebug += "------------------------------------------\n"
            self.print_debug(strDebug)

            return strSegment
        else:
            data = dict()
            data["id"] = slide.id
            data["endTime"] = slide.timecode + maxMovement * 200 + len(stepsList) * timeStep

            self.print_debug(data)

            return data

    def serial_animation(self, prevSlide, slide):
        startRow, startCol, endRow, endCol = self.find_animation_area(prevSlide, slide)
        time = slide.timecode
        direction = slide.animation['direction']
        timeStep = slide.animation['stepTime']
        stepsList = []
        stepDict = {}
        stepArray = prevSlide.images[:]
        nessSlide = slide.images[:]
        maxMovement = 0

        if direction == "lt_conner":
            side = True
            for row in range(startRow, endRow+1):
                if side:
                    for col in range(startCol, endCol+1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray

                            stepsList.append(copy.deepcopy(stepDict))
                    #side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray

                            stepsList.append(copy.deepcopy(stepDict))
                    side = True
        if direction == "rt_conner":
            side = False
            for row in range(startRow, endRow+1):
                if side:
                    for col in range(startCol, endCol+1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray

                            stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray

                            stepsList.append(copy.deepcopy(stepDict))
                    #side = True
        if direction == "lb_conner":
            side = True
            for row in range(endRow, startRow-1,  -1):
                if side:
                    for col in range(startCol, endCol+1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray

                            stepsList.append(copy.deepcopy(stepDict))
                    #side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray

                            stepsList.append(copy.deepcopy(stepDict))
                    side = True
        if direction == "rb_conner":
            side = False
            for row in range(endRow, startRow-1,  -1):
                if side:
                    for col in range(startCol, endCol+1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray

                            stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                        if movement > maxMovement:
                            maxMovement = movement
                        if self.callType == 'Full':
                            stepArray[row][col] = nessSlide[row][col]
                            stepDict['time'] = time
                            time += timeStep
                            stepDict['images'] = stepArray

                            stepsList.append(copy.deepcopy(stepDict))
                    #side = True

        if self.callType == 'Full':
            strSegment = ""
            for step in stepsList:
                strSegment += self.prepare_serial_data(step['time'], step['images'])

            strDebug = "+++\n+++ SLIDE ID {}\n+++\n".format(slide.id)
            strDebug += "------------------------------------------\n"
            for step in stepsList:
                strDebug += "timing: {}\n".format(step['time'])
                for row in step['images']:
                    strDebug += "{}\n".format(row)
                strDebug += "------------------------------------------\n"
            self.print_debug(strDebug)

            return strSegment
        else:
            data = dict()
            data["id"] = slide.id
            data["endTime"] = slide.timecode + maxMovement * 200 + len(stepsList) * timeStep

            self.print_debug(data)

            return data

    def noise_animation(self, prevSlide, slide):
        startRow, startCol, endRow, endCol = self.find_animation_area(prevSlide, slide)
        time = slide.timecode
        direction = slide.animation['direction']
        timeStep = slide.animation['stepTime']
        stepsList = []
        stepDict = {}
        stepArray = prevSlide.images[:]
        nessSlide = slide.images[:]
        maxMovement = 0

        NUMBER_OF_POINTS = 5
        listOfImg = []
        for row in range(startRow, endRow+1):
            for col in range(startCol, endCol+1):
                pos = (row, col)
                listOfImg.append(pos[:])

        shuffle(listOfImg)
        sizeOfList = len(listOfImg)

        for step in range(0, sizeOfList, NUMBER_OF_POINTS):
            for subStep in range(NUMBER_OF_POINTS):
                if listOfImg:
                    pos = listOfImg.pop()
                    movement = self.slice_movement(stepArray[pos[0]][pos[1]], nessSlide[pos[0]][pos[1]])
                    if movement > maxMovement:
                        maxMovement = movement
                    if self.callType == 'Full':
                        stepArray[pos[0]][pos[1]] = nessSlide[pos[0]][pos[1]]

            if self.callType == 'Full':
                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray
                stepsList.append(copy.deepcopy(stepDict))

        if self.callType == 'Full':
            strSegment = ""
            for step in stepsList:
                strSegment += self.prepare_serial_data(step['time'], step['images'])

            strDebug = "+++\n+++ SLIDE ID {}\n+++\n".format(slide.id)
            strDebug += "------------------------------------------\n"
            for step in stepsList:
                strDebug += "timing: {}\n".format(step['time'])
                for row in step['images']:
                    strDebug += "{}\n".format(row)
                strDebug += "------------------------------------------\n"
            self.print_debug(strDebug)

            return strSegment
        else:
            data = dict()
            data["id"] = slide.id
            data["endTime"] = slide.timecode + maxMovement * 200 + len(stepsList) * timeStep

            self.print_debug(data)

            return data

    def check_animation(self, prevSlide, slide):
        startRow, startCol, endRow, endCol = self.find_animation_area(prevSlide, slide)
        time = slide.timecode
        direction = slide.animation['direction']
        timeStep = slide.animation['stepTime']
        stepsList = []
        stepDict = {}
        stepArray = prevSlide.images[:]
        nessSlide = slide.images[:]
        maxMovement = 0

        side = True
        for row in range(startRow, endRow + 1):
            if side:
                for col in range(startCol, endCol + 1, 2):
                    movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                    if movement > maxMovement:
                        maxMovement = movement
                    if self.callType == 'Full':
                        stepArray[row][col] = nessSlide[row][col]
                side = False
            else:
                for col in range(startCol + 1, endCol + 1, 2):
                    movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                    if movement > maxMovement:
                        maxMovement = movement
                    if self.callType == 'Full':
                        stepArray[row][col] = nessSlide[row][col]
                side = True

        if self.callType == 'Full':
            stepDict['time'] = time
            time += timeStep
            stepDict['images'] = stepArray
            stepsList.append(copy.deepcopy(stepDict))

        side = False
        for row in range(startRow, endRow + 1):
            if side:
                for col in range(startCol, endCol + 1, 2):
                    movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                    if movement > maxMovement:
                        maxMovement = movement
                    if self.callType == 'Full':
                        stepArray[row][col] = nessSlide[row][col]
                side = False
            else:
                for col in range(startCol + 1, endCol + 1, 2):
                    movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                    if movement > maxMovement:
                        maxMovement = movement
                    if self.callType == 'Full':
                        stepArray[row][col] = nessSlide[row][col]
                side = True

        if self.callType == 'Full':
            stepDict['time'] = time
            time += timeStep
            stepDict['images'] = stepArray
            stepsList.append(copy.deepcopy(stepDict))

        if self.callType == 'Full':
            strSegment = ""
            for step in stepsList:
                strSegment += self.prepare_serial_data(step['time'], step['images'])

            strDebug = "+++\n+++ SLIDE ID {}\n+++\n".format(slide.id)
            strDebug += "------------------------------------------\n"
            for step in stepsList:
                strDebug += "timing: {}\n".format(step['time'])
                for row in step['images']:
                    strDebug += "{}\n".format(row)
                strDebug += "------------------------------------------\n"
            self.print_debug(strDebug)

            return strSegment
        else:
            data = dict()
            data["id"] = slide.id
            data["endTime"] = slide.timecode + maxMovement * 200 + len(stepsList) * timeStep

            self.print_debug(data)

            return data
        pass

    def arrow_animation(self, prevSlide, slide):
        startRow, startCol, endRow, endCol = self.find_animation_area(prevSlide, slide)
        time = slide.timecode
        direction = slide.animation['direction']
        timeStep = slide.animation['stepTime']
        stepsList = []
        stepDict = {}
        stepArray = prevSlide.images[:]
        nessSlide = slide.images[:]
        maxMovement = 0

        if (endRow - startRow + 1) % 2 != 0:
            r1 = startRow + int((endRow - startRow) / 2)
            r2 = startRow + int((endRow - startRow) / 2)
        else:
            r1 = startRow + int((endRow - startRow) / 2)
            r2 = r1 + 1

        if direction == 'left_right':
            for step in range(startCol, endCol + int((r1 + r2) / 2) + 1):
                for col in range(startCol, step + 1):
                    for row in range(step - col + 1):
                        if (startRow <= (r1 - row) <= endRow) and (startCol <= col <= endCol):
                            movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[r1 - row][col] = nessSlide[r1 - row][col]
                        if (startRow <= (r2 + row) <= endRow) and (startCol <= col <= endCol):
                            movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[r2 + row][col] = nessSlide[r2 + row][col]
                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))
        elif direction == 'right_left':
            for step in range(startCol, endCol + int((r1 + r2) / 2) + 1):
                for col in range(endCol, endCol - step - 1, -1):
                    for row in range(col - (endCol - step) + 1):
                        if (startRow <= (r1 - row) <= endRow) and (startCol <= col <= endCol):
                            movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[r1 - row][col] = nessSlide[r1 - row][col]
                        if (startRow <= (r2 + row) <= endRow) and (startCol <= col <= endCol):
                            movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[r2 + row][col] = nessSlide[r2 + row][col]
                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray
                    stepsList.append(copy.deepcopy(stepDict))

        if self.callType == 'Full':
            strSegment = ""
            for step in stepsList:
                strSegment += self.prepare_serial_data(step['time'], step['images'])

            strDebug = "+++\n+++ SLIDE ID {}\n+++\n".format(slide.id)
            strDebug += "------------------------------------------\n"
            for step in stepsList:
                strDebug += "timing: {}\n".format(step['time'])
                for row in step['images']:
                    strDebug += "{}\n".format(row)
                strDebug += "------------------------------------------\n"
            self.print_debug(strDebug)

            return strSegment
        else:
            data = dict()
            data["id"] = slide.id
            data["endTime"] = slide.timecode + maxMovement * 200 + len(stepsList) * timeStep

            self.print_debug(data)

            return data

    def conner_animation(self, prevSlide, slide):
        startRow, startCol, endRow, endCol = self.find_animation_area(prevSlide, slide)
        time = slide.timecode
        direction = slide.animation['direction']
        timeStep = slide.animation['stepTime']
        stepsList = []
        stepDict = {}
        stepArray = prevSlide.images[:]
        nessSlide = slide.images[:]
        maxMovement = 0
        mostDirection = True  # for horizontal

        if direction == "lt_conner":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
                print("vertical direction")
            else:
                mostDirection = True
                print("horizontal direction")

            if mostDirection:
                for col in range(startCol, endCol + 1):
                    for col1 in range(startCol, col + 1):
                        for row1 in range(startRow, startRow + col - startCol + 1):
                            if row1 <= endRow and row1 >= startRow:
                                movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                                if movement > maxMovement:
                                    maxMovement = movement
                                if self.callType == 'Full':
                                    stepArray[row1][col1] = nessSlide[row1][col1]
                    if self.callType == 'Full':
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(startRow, endRow + 1):
                    for row1 in range(startRow, row + 1):
                        for col1 in range(startCol, startCol + (row - startRow) + 1):
                            if col1 <= endCol and col1 >= startCol:
                                movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                                if movement > maxMovement:
                                    maxMovement = movement
                                if self.callType == 'Full':
                                    stepArray[row1][col1] = nessSlide[row1][col1]
                    if self.callType == 'Full':
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))

        elif direction == "rt_conner":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
            else:
                mostDirection = True
            if mostDirection:
                for col in range(endCol, startCol - 1, -1):
                    for col1 in range(endCol, col - 1, -1):
                        for row1 in range(startRow, startRow + (endCol - col) + 1):
                            if row1 <= endRow and row1 >= startRow:
                                movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                                if movement > maxMovement:
                                    maxMovement = movement
                                if self.callType == 'Full':
                                    stepArray[row1][col1] = nessSlide[row1][col1]
                    if self.callType == 'Full':
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(startRow, endRow + 1):
                    for row1 in range(startRow, row + 1):
                        for col1 in range(endCol, endCol - (row - startRow) - 1, -1):
                            if col1 <= endCol and col1 >= startCol:
                                movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                                if movement > maxMovement:
                                    maxMovement = movement
                                if self.callType == 'Full':
                                    stepArray[row1][col1] = nessSlide[row1][col1]
                    if self.callType == 'Full':
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))

        if direction == "lb_conner":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
            else:
                mostDirection = True

            if mostDirection:
                for col in range(startCol, endCol + 1):
                    for col1 in range(startCol, col + 1):
                        for row1 in range(endRow, endRow - (col - startCol) - 1, -1):
                            if row1 <= endRow and row1 >= startRow:
                                movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                                if movement > maxMovement:
                                    maxMovement = movement
                                if self.callType == 'Full':
                                    stepArray[row1][col1] = nessSlide[row1][col1]
                    if self.callType == 'Full':
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(endRow, startRow - 1, -1):
                    for row1 in range(endRow, row - 1, -1):
                        for col1 in range(startCol, startCol + (endRow - row) + 1):
                            if col1 <= endCol and col1 >= startCol:
                                movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                                if movement > maxMovement:
                                    maxMovement = movement
                                if self.callType == 'Full':
                                    stepArray[row1][col1] = nessSlide[row1][col1]
                    if self.callType == 'Full':
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
        elif direction == "rb_conner":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
            else:
                mostDirection = True

            if mostDirection:
                for col in range(endCol, startCol - 1, -1):
                    for col1 in range(endCol, col - 1, -1):
                        for row1 in range(endRow, endRow - (endCol - col) - 1, -1):
                            if row1 <= endRow and row1 >= startRow:
                                movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                                if movement > maxMovement:
                                    maxMovement = movement
                                if self.callType == 'Full':
                                    stepArray[row1][col1] = nessSlide[row1][col1]
                    if self.callType == 'Full':
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(endRow, startRow - 1, -1):
                    for row1 in range(endRow, row - 1, -1):
                        for col1 in range(endCol, endCol - (endRow - row) - 1, -1):
                            if col1 <= endCol and col1 >= startCol:
                                movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                                if movement > maxMovement:
                                    maxMovement = movement
                                if self.callType == 'Full':
                                    stepArray[row1][col1] = nessSlide[row1][col1]
                    if self.callType == 'Full':
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
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
                            movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                            if movement > maxMovement:
                                maxMovement = movement
                            if self.callType == 'Full':
                                stepArray[row][col] = nessSlide[row][col]
                if self.callType == 'Full':
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))

        if self.callType == 'Full':
            strSegment = ""
            for step in stepsList:
                strSegment += self.prepare_serial_data(step['time'], step['images'])

            strDebug = "+++\n+++ SLIDE ID {}\n+++\n".format(slide.id)
            strDebug += "------------------------------------------\n"
            for step in stepsList:
                strDebug += "timing: {}\n".format(step['time'])
                for row in step['images']:
                    strDebug += "{}\n".format(row)
                strDebug += "------------------------------------------\n"
            self.print_debug(strDebug)

            return strSegment
        else:
            data = dict()
            data["id"] = slide.id
            data["endTime"] = slide.timecode + maxMovement * 200 + len(stepsList) * timeStep

            self.print_debug(data)

            return data

    def find_animation_area(self, prevSlide, nextSlide):
        maxRow = 0
        maxCol = 0
        minRow = len(prevSlide.images)
        minCol = len(prevSlide.images[0])

        for row in range(self.height):
            for col in range(self.width):
                if prevSlide.images[row][col] != nextSlide.images[row][col]:
                    if row > maxRow:
                        maxRow = row
                    if row < minRow:
                        minRow = row
                    if col > maxCol:
                        maxCol = col
                    if col < minCol:
                        minCol = col

        return(minRow, minCol, maxRow, maxCol)

    def slice_movement(self, start, end):
        if start < 20 and end < 20:
            if end < start:
                return 20 - start + end
            else:
                return end - start
        else:
            modStart = int(start / 20)
            modEnd = int(end / 20)
            if modEnd < modStart:
                return 20 - modStart + modEnd + 20 * (end % 20)
            else:
                return modEnd - modStart + 20 * (end % 20)

    def prepare_serial_data(self, time, array):
        serialList = []
        for l in array:
            serialList.extend(l)

        message = ""
        message += str(time)
        message += ";"
        for item in serialList:
            message += str(item)
            message += ","
        message += '\n'

        return message

    def print_debug(self, s):
        print("<div class=\"MyPyDebug\">")
        print(s)
        print("</div>")

    def print_response_animation_time(self, s):
        print("<div class=\"animationTime\">", end="")
        print(s)
        print("</div>")

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    imgProcessWindow = ProcessJSON()
    imgProcessWindow.show()
    sys.exit(app.exec_())
