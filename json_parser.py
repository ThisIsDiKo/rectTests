import json
import copy
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
                else:
                    anim_type = "check"

                anim_time = data['animation'][0]['time']
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
                slide['animation'] = None



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

            if self.slides[slideNum]['animation']['type'] == 'waterfall':
                self.waterfall_animation(self.slides[slideNum-1]['images'],
                                         self.slides[slideNum]['images'],
                                         self.slides[slideNum]['timecode'],
                                         self.slides[slideNum]['animation']['time'],
                                         self.slides[slideNum]['animation']['direction'],
                                         (minRow, minCol),
                                         (maxRow, maxCol))
            elif self.slides[slideNum]['animation']['type'] == 'wave':
                self.wave_animation(self.slides[slideNum-1]['images'],
                                         self.slides[slideNum]['images'],
                                         self.slides[slideNum]['timecode'],
                                         self.slides[slideNum]['animation']['time'],
                                         self.slides[slideNum]['animation']['direction'],
                                         (minRow, minCol),
                                         (maxRow, maxCol))

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

    def waterfall_animation(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]

        if direction == "up_down":
            for row in range(startRow, endRow + 1):
                for col in range(startCol, endCol + 1):
                    stepArray[row][col] = nessSlide[row][col]

                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray

                stepsList.append(copy.deepcopy(stepDict))

        elif direction == "down_up":
            for row in range(endRow, startRow+1, - 1):
                for col in range(startCol, endCol + 1):
                    stepArray[row][col] = nessSlide[row][col]

                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray

                stepsList.append(copy.deepcopy(stepDict))
        elif direction == "left_right":
            for col in range(startCol, endCol + 1):
                for row in range(startRow, endRow + 1):
                    stepArray[row][col] = nessSlide[row][col]

                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray

                stepsList.append(copy.deepcopy(stepDict))

        elif direction == "right_left":
            for col in range(endCol, startCol + 1, -1):
                for row in range(startRow, endRow + 1):
                    stepArray[row][col] = nessSlide[row][col]

                stepDict['time'] = time
                time += timeStep
                stepDict['images'] = stepArray

                stepsList.append(copy.deepcopy(stepDict))


        print("------------------------------------------")
        for step in stepsList:
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
                            print(col, col1, row1)
                            if row1 <= endRow and row1 >= startRow:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(startRow, endRow + 1):
                    for row1 in range(row + 1):
                        for col1 in range(row + 1):
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
                    for row1 in range(row + 1):
                        for col1 in range(endCol, endCol - row - 1, -1):
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
                        for row1 in range(endRow, endRow - endCol-col-1, -1):
                            if row1 <= endRow and row1 >= startRow:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(endRow, startRow-1, -1):
                    for row1 in range(endRow, row-1, -1):
                        for col1 in range((row-endRow) + 1):
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
                        for row1 in range(endCol, col-1, -1):
                            if row1 <= endRow and row1 >= startRow:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))
            else:
                for row in range(endRow, startRow-1, -1):
                    for row1 in range(endRow, row-1, -1):
                        for col1 in range(endRow, row-1, -1):
                            if col1 <= endCol and col1 >= startCol:
                                stepArray[row1][col1] = nessSlide[row1][col1]
                    stepDict['time'] = time
                    time += timeStep
                    stepDict['images'] = stepArray

                    stepsList.append(copy.deepcopy(stepDict))

        print("------------------------------------------")
        for step in stepsList:
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

    def serial_animation(self, prevSlide, nessSlide, startTime, timeStep, direction, startPos, endPos):
        startRow, startCol = startPos
        endRow, endCol = endPos
        time = startTime

        stepsList = []
        stepDict = {}
        stepArray = prevSlide[:]



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    imgProcessWindow = ProcessJSON()
    imgProcessWindow.show()
    sys.exit(app.exec_())
