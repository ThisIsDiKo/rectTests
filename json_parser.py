import json
import copy
from random import shuffle
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy, QLineEdit, QComboBox, QPushButton,
                             QHBoxLayout, QVBoxLayout, QWidget)
"""
data = None

with open('test_anim.json', 'r') as read_file:
    data = json.load(read_file)

slide = data[0]
slideData = [int(i) for i in slide['images']]

#print(slideData)
#print(len(slideData))

t = []
picture = []
counter = 0
for img in slideData:
    t.append(img)
    counter += 1
    if counter == 25:
        counter = 0
        picture.append(t)
        t = []

for i in picture:
    print(i)
"""


class ProcessJSON(QWidget):
    def __init__(self):
        super(ProcessJSON, self).__init__()

        self.scenario = Scenario()


        self.open_file()

        self.scenario.check_timecodes()
        self.scenario.prepare_animation()

    def open_file(self):
        print("Open file")
        fileName, _ = QFileDialog.getOpenFileName(self, "Открыть файл", QDir.currentPath())
        print(fileName)
        if fileName:
            data = None
            with open(fileName, 'r') as readFile:
                data = json.load(readFile)

            self.scenario.init_slides(data)
            print("data read")


class Scenario:
    def __init__(self):
        self.width = 25
        self.height = 10

        self.fileToWrite = None

        try:
            self.fileToWrite = open('sc.txt', 'w')
        except:
            print("can't open file")

        self.slides = []
        self.rawAnimation = []

    def init_slides(self, s):
        preSlides = s
        slide = {}

        for data in preSlides:

            #Копируем Id
            slide['id'] = int(data['id'])

            #Преобразование времени
            l = data['timecode'].split(':')
            minutes = int(l[0])
            seconds = int(l[1])
            milliseconds = int(l[2])
            slide['timecode'] = minutes * 60 * 1000 + seconds * 1000 + milliseconds

            #Преобразование одномерного массива в двумерный и перевод в числовые значения
            slide['images'] = []
            t = []
            counter = 0
            for img in data['images']:
                t.append(int(img) - 1)
                counter += 1
                if counter == 25:
                    counter = 0
                    slide['images'].append(t)
                    t = []

            # Преобразование анимации
            try:
                animation = data['animation']
            except:
                animation = "None"
            print("animations is %s" % animation)
            print(animation == "None")
            if animation != "None":
                anim_type = data['animation'][0]['type']
                if anim_type == '1':
                    anim_type = 'waterfall'
                elif anim_type == '2':
                    anim_type = 'wave'
                elif anim_type == '3':
                    anim_type = 'snake'
                elif anim_type == '4':
                    anim_type = 'serial'
                elif anim_type == '5':
                    anim_type = 'noise'
                elif anim_type == '6':
                    anim_type = "check"
                elif anim_type == '7':
                    anim_type = 'arrow'

                try:
                    anim_time = data['animation'][0]['time']
                except:
                    anim_time = None

                if anim_time is not None:
                    anim_time = int(anim_time)
                else:
                    anim_time = 500

                anim_rounds = data['animation'][0]['rpm']

                if anim_rounds is not None:
                    anim_rounds = int(anim_rounds)
                else:
                    anim_rounds = 0

                anim_direction = None

                try:
                    anim_direction = data['animation'][0]['direction1']
                    if anim_direction == '1':
                        anim_direction = 'up_down'
                    elif anim_direction == '2':
                        anim_direction = 'down_up'
                    elif anim_direction == '3':
                        anim_direction = 'left_right'
                    elif anim_direction == '4':
                        anim_direction = 'right_left'
                except:
                    print('no parameter direction1')

                try:
                    anim_direction = data['animation'][0]['direction2']
                    if anim_direction == '1':
                        anim_direction = 'lt_conner'
                    elif anim_direction == '2':
                        anim_direction = 'rt_conner'
                    elif anim_direction == '3':
                        anim_direction = 'lb_conner'
                    elif anim_direction == '4':
                        anim_direction = 'rb_conner'
                    elif anim_direction == '5':
                        anim_direction = 'center'
                except:
                    print('no parameter direction2')


                animation = {}
                animation['type'] = anim_type
                animation['time'] = anim_time
                animation['rounds'] = anim_rounds
                animation['direction'] = anim_direction

                slide['animation'] = animation.copy()
            else:
                slide['animation'] = 'None'



            self.slides.append(slide.copy())

        print(self.slides[0])
        for r in self.slides[0]['images']:
            print(r)
        print(self.slides[0]['animation'])

    def check_timecodes(self):
        prevTimecode = 0

        if not self.slides:
            print("slides are empty")
            return 2

        for slide in self.slides:
            if slide['timecode'] >= prevTimecode:
                prevTimecode = slide['timecode']
            else:
                print("error id %s has wrong timecode" % slide['id'])
                return 1
        print("everything is ok")
        return 0

    def prepare_animation(self):

        self.write_data_to_file(self.prepare_serial_data(self.slides[0]['timecode'], self.slides[0]['images']))

        for slideNum in range(1, len(self.slides)):
            maxRow = 0
            maxCol = 0
            minRow = self.height
            minCol = self.width

            for row in range(self.height):
                for col in range(self.width):
                    if self.slides[slideNum-1]['images'][row][col] != self.slides[slideNum]['images'][row][col]:
                        if row > maxRow:
                            maxRow = row
                        if row < minRow:
                            minRow = row
                        if col > maxCol:
                            maxCol = col
                        if col < minCol:
                            minCol = col
            print("between {} and {}: {}, {}".format(slideNum-1, slideNum, (minRow, minCol), (maxRow, maxCol)))

            if self.slides[slideNum]['animation'] != 'None':
                if self.slides[slideNum]['animation']['type'] == 'waterfall':
                    self.waterfall_animation(self.slides[slideNum-1]['images'],
                                             self.slides[slideNum]['images'],
                                             self.slides[slideNum]['timecode'],
                                             self.slides[slideNum]['animation']['time'],
                                             self.slides[slideNum]['animation']['direction'],
                                             (minRow, minCol),
                                             (maxRow, maxCol))
                elif self.slides[slideNum]['animation']['type'] == 'wave':
                    self.wave_2_animation(self.slides[slideNum-1]['images'],
                                             self.slides[slideNum]['images'],
                                             self.slides[slideNum]['timecode'],
                                             self.slides[slideNum]['animation']['time'],
                                             self.slides[slideNum]['animation']['direction'],
                                             (minRow, minCol),
                                             (maxRow, maxCol))
                elif self.slides[slideNum]['animation']['type'] == 'snake':
                    self.snake_animation(self.slides[slideNum-1]['images'],
                                             self.slides[slideNum]['images'],
                                             self.slides[slideNum]['timecode'],
                                             self.slides[slideNum]['animation']['time'],
                                             self.slides[slideNum]['animation']['direction'],
                                             (minRow, minCol),
                                             (maxRow, maxCol))
                elif self.slides[slideNum]['animation']['type'] == 'serial':
                    self.serial_animation(self.slides[slideNum-1]['images'],
                                             self.slides[slideNum]['images'],
                                             self.slides[slideNum]['timecode'],
                                             self.slides[slideNum]['animation']['time'],
                                             self.slides[slideNum]['animation']['direction'],
                                             (minRow, minCol),
                                             (maxRow, maxCol))
                elif self.slides[slideNum]['animation']['type'] == 'noise':
                    self.noise_animation(self.slides[slideNum-1]['images'],
                                             self.slides[slideNum]['images'],
                                             self.slides[slideNum]['timecode'],
                                             self.slides[slideNum]['animation']['time'],
                                             self.slides[slideNum]['animation']['direction'],
                                             (minRow, minCol),
                                             (maxRow, maxCol))
                elif self.slides[slideNum]['animation']['type'] == 'check':
                    self.check_animation(self.slides[slideNum-1]['images'],
                                             self.slides[slideNum]['images'],
                                             self.slides[slideNum]['timecode'],
                                             self.slides[slideNum]['animation']['time'],
                                             self.slides[slideNum]['animation']['direction'],
                                             (minRow, minCol),
                                             (maxRow, maxCol))
                elif self.slides[slideNum]['animation']['type'] == 'arrow':
                    self.horizontal_arrow(self.slides[slideNum-1]['images'],
                                             self.slides[slideNum]['images'],
                                             self.slides[slideNum]['timecode'],
                                             self.slides[slideNum]['animation']['time'],
                                             self.slides[slideNum]['animation']['direction'],
                                             (minRow, minCol),
                                             (maxRow, maxCol))
            else:
                self.write_data_to_file(self.prepare_serial_data(self.slides[slideNum]['timecode'], self.slides[slideNum]['images']))

        self.fileToWrite.close()

        try:
            f = open('sc.txt', 'rb+')
            f.seek()
            f.truncate()
            f.close()
        except:
            print("can't open file")



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

    def write_data_to_file(self, s):
        print(s)
        if self.fileToWrite:
            self.fileToWrite.write(s)

    def waterfall_animation(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]
        maxMovement = 0

        if direction == "up_down":
            for row in range(startRow, endRow + 1):
                for col in range(startCol, endCol + 1):
                    movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                    if movement > maxMovement:
                        maxMovement = movement
                    stepArray[row][col] = nessSlide[row][col]

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
                    stepArray[row][col] = nessSlide[row][col]

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
                    stepArray[row][col] = nessSlide[row][col]

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
                    stepArray[row][col] = nessSlide[row][col]

                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray

                stepsList.append(copy.deepcopy(stepDict))


        print("------------------------------------------")
        print("Animation paraments:")
        print("\tMax movement: {}\n\tSteps: {}".format(maxMovement, len(stepsList)))
        print("\tAnimationTime: {}".format(maxMovement*0.2 + len(stepsList)*timeStep/1000))
        lOfData = []
        data = {}
        data["id"] = 1
        data["endTime"] = maxMovement*0.2 + len(stepsList)*timeStep/1000
        lOfData.append(copy.deepcopy(data))
        data["id"] = 2
        data["endTime"] = 15
        lOfData.append(copy.deepcopy(data))
        json_data = json.dumps(lOfData)
        print(json_data)
        for step in stepsList:
            self.write_data_to_file(self.prepare_serial_data(step['time'], step['images']))
            print("timing: {}".format(step['time']))
            for row in step['images']:
                print(row)
            print("------------------------------------------")

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


    def wave_2_animation(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]
        maxMovement = 0

        mostDirection = True #for horizontal

        if direction == "lt_conner":
            for col in range(startCol, endCol + (endRow - startRow) + 1):
                for col1 in range(startCol, col + 1):
                    for row1 in range(startRow, startRow + col - col1 + 1):
                        if (startRow <= row1 <= endRow) and (startCol <= col1 <= endCol):
                            movement = self.slice_movement(stepArray[row1][col1], nessSlide[row1][col1])
                            if movement > maxMovement:
                                maxMovement = movement
                            stepArray[row1][col1] = nessSlide[row1][col1]
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
                            stepArray[row1][col1] = nessSlide[row1][col1]
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
                            stepArray[row1][col1] = nessSlide[row1][col1]
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
                            stepArray[row1][col1] = nessSlide[row1][col1]
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

            print(st, r1, r2, c1, c2)

            for step in range(st+1):
                for col in range(c1-step, c2+step+1):
                    for row in range(r1-step, r2+step+1):
                        if (row <= endRow and row >= startRow) and (col <= endCol and col >= startCol):
                            movement = self.slice_movement(stepArray[row][col], nessSlide[row][col])
                            if movement > maxMovement:
                                maxMovement = movement
                            stepArray[row][col] = nessSlide[row][col]
                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray

                stepsList.append(copy.deepcopy(stepDict))

        print("------------------------------------------")
        print("Animation paraments:")
        print("\tMax movement: {}\n\tSteps: {}".format(maxMovement, len(stepsList)))
        print("\tAnimationTime: {}".format(maxMovement * 0.2 + len(stepsList) * timeStep / 1000))
        for step in stepsList:
            self.write_data_to_file(self.prepare_serial_data(step['time'], step['images']))
            print("timing: {}".format(step['time']))
            for row in step['images']:
                print(row)
            print("------------------------------------------")

    def horizontal_arrow(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]

        if (endRow - startRow + 1) % 2 != 0:
            r1 = startRow + int((endRow - startRow) / 2)
            r2 = startRow + int((endRow - startRow) / 2)
        else:
            r1 = startRow + int((endRow - startRow) / 2)
            r2 = r1 + 1

        if direction == 'left_right':
            for step in range(startCol, endCol+int((r1+r2)/2)+1):
                for col in range(startCol, step+1):
                    for row in range(step-col+1):
                        if (startRow <= (r1 - row) <= endRow) and (startCol <= col <= endCol):
                            stepArray[r1 - row][col] = nessSlide[r1 - row][col]
                        if (startRow <= (r2 + row) <= endRow) and (startCol <= col <= endCol):
                            stepArray[r2 + row][col] = nessSlide[r2 + row][col]
                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray
                stepsList.append(copy.deepcopy(stepDict))
        elif direction == 'right_left':
            for step in range(startCol, endCol+int((r1+r2)/2)+1):
                for col in range(endCol, endCol-step-1, -1):
                    for row in range(col - (endCol - step)+1):
                        if (startRow <= (r1 - row) <= endRow) and (startCol <= col <= endCol):
                            stepArray[r1 - row][col] = nessSlide[r1 - row][col]
                        if (startRow <= (r2 + row) <= endRow) and (startCol <= col <= endCol):
                            stepArray[r2 + row][col] = nessSlide[r2 + row][col]
                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray
                stepsList.append(copy.deepcopy(stepDict))

        print("------------------------------------------")
        for step in stepsList:
            # self.write_data_to_file(self.prepare_serial_data(step['time'], step['images']))
            print("timing: {}".format(step['time']))
            for row in step['images']:
                print(row)
            print("------------------------------------------")

    def wave_animation(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]

        mostDirection = True #for horizontal

        if direction == "lt_conner":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
                print("vertical direction")
            else:
                mostDirection = True
                print("horizontal direction")

            if mostDirection:
                for col in range(startCol, endCol+1):
                    for col1 in range(startCol, col+1):
                        for row1 in range(startRow, startRow+col-startCol+1):
                            if row1 <= endRow and row1 >= startRow:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(startRow, endRow + 1):
                    for row1 in range(startRow, row + 1):
                        for col1 in range(startCol, startCol + (row - startRow) + 1):
                            if col1 <= endCol and col1 >= startCol:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))

        elif direction == "rt_conner":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
                print("vertical direction")
            else:
                mostDirection = True
                print("horizontal direction")
            """
            if mostDirection:
                for col in range(endCol, startCol-1, -1):
                    print(col, end=' -- ')
                    for col1 in range(endCol, col-1, -1):
                        print(col1, end=' ++ \n')
                        for row1 in range((col1-col)+1):
                            if row1 <= endRow and row1 >= startRow:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(startRow, endRow + 1):
                    for row1 in range(row + 1):
                        for col1 in range(endCol, row-1, -1):
                            if col1 <= endCol and col1 >= startCol:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
            """
            if mostDirection:
                for col in range(endCol, startCol - 1, -1):
                    for col1 in range(endCol, col - 1, -1):
                        for row1 in range(startRow, startRow+(endCol - col) + 1):
                            if row1 <= endRow and row1 >= startRow:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(startRow, endRow + 1):
                    for row1 in range(startRow, row + 1):
                        for col1 in range(endCol, endCol - (row - startRow) - 1, -1):
                            if col1 <= endCol and col1 >= startCol:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))

        if direction == "lb_conner":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
                print("vertical direction")
            else:
                mostDirection = True
                print("horizontal direction")

            if mostDirection:
                for col in range(startCol, endCol+1):
                    for col1 in range(startCol, col+1):
                        for row1 in range(endRow, endRow - (col-startCol)-1, -1):
                            if row1 <= endRow and row1 >= startRow:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(endRow, startRow-1, -1):
                    for row1 in range(endRow, row-1, -1):
                        for col1 in range(startCol, startCol + (endRow - row) + 1):
                            if col1 <= endCol and col1 >= startCol:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
        elif direction == "rb_conner":
            if (endRow - startRow) > (endCol - startCol):
                mostDirection = False
                print("vertical direction")
            else:
                mostDirection = True
                print("horizontal direction")

            if mostDirection:
                for col in range(endCol, startCol-1, -1):
                    for col1 in range(endCol, col-1, -1):
                        for row1 in range(endRow, endRow - (endCol-col) - 1, -1):
                            if row1 <= endRow and row1 >= startRow:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(endRow, startRow-1, -1):
                    for row1 in range(endRow, row-1, -1):
                        for col1 in range(endCol, endCol - (endRow - row)-1, -1):
                            if col1 <= endCol and col1 >= startCol:
                                stepArray[row1][col1] = nessSlide[row1][col1]
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

            print(st, r1, r2, c1, c2)

            for step in range(st+1):
                for col in range(c1-step, c2+step+1):
                    for row in range(r1-step, r2+step+1):
                        if (row <= endRow and row >= startRow) and (col <= endCol and col >= startCol):
                            stepArray[row][col] = nessSlide[row][col]
                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray

                stepsList.append(copy.deepcopy(stepDict))

        print("------------------------------------------")
        for step in stepsList:
            self.write_data_to_file(self.prepare_serial_data(step['time'], step['images']))
            print("timing: {}".format(step['time']))
            for row in step['images']:
                print(row)
            print("------------------------------------------")


    def snake_animation(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]

        if direction == "lt_conner":
            side = True
            for row in range(startRow, endRow+1):
                if side:
                    for col in range(startCol, endCol+1):
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
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
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
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
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
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
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    side = True
        print("------------------------------------------")
        for step in stepsList:
            self.write_data_to_file(self.prepare_serial_data(step['time'], step['images']))
            print("timing: {}".format(step['time']))
            for row in step['images']:
                print(row)
            print("------------------------------------------")

    def serial_animation(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]

        if direction == "lt_conner":
            side = True
            for row in range(startRow, endRow+1):
                if side:
                    for col in range(startCol, endCol+1):
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    #side = False
                else:
                    for col in range(endCol, startCol-1, -1):
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
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
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
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    #side = False
                else:
                    for col in range(endCol, startCol-1, -1):
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
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    side = False
                else:
                    for col in range(endCol, startCol-1, -1):
                        stepArray[row][col] = nessSlide[row][col]
                        stepDict['time'] = time
                        time += timeStep
                        stepDict['images'] = stepArray

                        stepsList.append(copy.deepcopy(stepDict))
                    #side = True
        print("------------------------------------------")
        for step in stepsList:
            self.write_data_to_file(self.prepare_serial_data(step['time'], step['images']))
            print("timing: {}".format(step['time']))
            for row in step['images']:
                print(row)
            print("------------------------------------------")

    def noise_animation(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        print("noise animation")
        NUMBER_OF_POINTS = 5

        listOfImg = []

        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]

        for row in range(startRow, endRow+1):
            for col in range(startCol, endCol+1):
                pos = (row, col)
                listOfImg.append(pos[:])

        shuffle(listOfImg)

        sizeOfList = len(listOfImg)
        print(sizeOfList)
        for i in listOfImg:
            print(i)

        for step in range(0, sizeOfList, NUMBER_OF_POINTS):
            for subStep in range(NUMBER_OF_POINTS):
                if listOfImg:
                    pos = listOfImg.pop()
                    print('---', pos)
                    stepArray[pos[0]][pos[1]] = nessSlide[pos[0]][pos[1]]

            stepDict['time'] = time
            time += timeStep
            stepDict['images'] = stepArray
            stepsList.append(copy.deepcopy(stepDict))
            print(len(stepsList))

        print("------------------------------------------")
        for step in stepsList:
            self.write_data_to_file(self.prepare_serial_data(step['time'], step['images']))
            print("timing: {}".format(step['time']))
            for row in step['images']:
                print(row)
            print("------------------------------------------")

    def check_animation(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        print("check animation")

        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]
        side = True
        for row in range(startRow, endRow+1):
            if side:
                for col in range(startCol, endCol+1, 2):
                    stepArray[row][col] = nessSlide[row][col]
                side = False
            else:
                for col in range(startCol+1, endCol+1, 2):
                    stepArray[row][col] = nessSlide[row][col]
                side = True

        stepDict['time'] = time
        time += timeStep
        stepDict['images'] = stepArray
        stepsList.append(copy.deepcopy(stepDict))

        side = False
        for row in range(startRow, endRow + 1):
            if side:
                for col in range(startCol, endCol + 1, 2):
                    stepArray[row][col] = nessSlide[row][col]
                side = False
            else:
                for col in range(startCol + 1, endCol + 1, 2):
                    stepArray[row][col] = nessSlide[row][col]
                side = True

        stepDict['time'] = time
        time += timeStep
        stepDict['images'] = stepArray
        stepsList.append(copy.deepcopy(stepDict))

        print("------------------------------------------")
        for step in stepsList:
            self.write_data_to_file(self.prepare_serial_data(step['time'], step['images']))
            print("timing: {}".format(step['time']))
            for row in step['images']:
                print(row)
            print("------------------------------------------")



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    imgProcessWindow = ProcessJSON()
    imgProcessWindow.show()
    sys.exit(app.exec_())
