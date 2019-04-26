import threading
import sqlite3
import StringIO
import numpy as np
import Image
import cv2
from PyQt4 import QtCore, QtGui, uic
import Queue
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import QPixmap
import serial
from serial.tools import list_ports
from PyQt4.QtGui import QApplication

running = False
thd = False
remove = False
captureFrame = False
imList = []
imNo = 0
capture_thread = None
q = Queue.Queue()
hue=0.000
ammountOfBilirubin=0.000
recognizer = cv2.createLBPHFaceRecognizer()

def grab(cam, queue):
    global running
    global hue
    global captureFrame
    global ammountOfBilirubin
    capture = cv2.VideoCapture(0)

    while (running):
        frame = {}
        capture.grab()
        retval, img = capture.read()
        
        while img is None:
            retval, img = capture.read()
        frame["img"] = img

        if queue.qsize() < 10:
            queue.put(frame)
        else:
            pass

        if captureFrame:
            
            running=False
            img1=img.copy()
            img2=img.copy()
            img1 = cv2.medianBlur(img1,5)
            img[img1[:,:,1] <= 140]= 0
            img[img[:,:,2] <= 150]= 0
            hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
            lower_value = np.array([20,10,180])
            upper_value = np.array([100,200,255])
            mask = cv2.inRange(hsv, lower_value, upper_value)
            res = cv2.bitwise_and(img,img, mask= mask)
            u= hsv[res[:,:,0] >0 ]
            c=img2[res[:,:,0] >0 ]
            average_color = np.average(u, axis=0)
            [hue, s, v] = average_color
            
            if (hue <70):
                ammountOfBilirubin = -0.00029259 * hue * hue * hue + 0.039715* hue * hue - 2.4269* hue + 74.806
            elif (70<= hue <76):
                ammountOfBilirubin = -0.029391 * hue * hue + 4.1877 * hue - 148.05
            elif (76<= hue <90):
                ammountOfBilirubin = -0.071897* hue + 6.5784
            
            
            print hue
            print len(u)
            print u.size
            print u.mean()
            print average_color
            cv2.imshow("image1", mask)
            frame["img"] = res

            if queue.qsize() < 10:
                queue.put(frame)
            else:
                pass


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_Form(object):
    def __init__(self):
        self.timer = None

    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Jaundice"))
        Form.resize(522, 459)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.ImgWidget = QtGui.QLabel(self.groupBox)
        self.ImgWidget.setObjectName(_fromUtf8("ImgWidget"))
        self.horizontalLayout_3.addWidget(self.ImgWidget)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.AddButton = QtGui.QPushButton(Form)
        self.AddButton.setObjectName(_fromUtf8("AddButton"))
        self.horizontalLayout.addWidget(self.AddButton)
        self.TextLabel = QtGui.QLabel(Form)
        self.AddButton.setObjectName(_fromUtf8("TextLabel"))
        self.horizontalLayout.addWidget(self.TextLabel)
        self.TextLabel2 = QtGui.QLabel(Form)
        self.AddButton.setObjectName(_fromUtf8("TextLabel2"))
        self.horizontalLayout.addWidget(self.TextLabel2)
        self.TextLabel3 = QtGui.QLabel(Form)
        self.AddButton.setObjectName(_fromUtf8("TextLabel3"))
        self.horizontalLayout.addWidget(self.TextLabel3)
        self.ExitButton = QtGui.QPushButton(Form)
        self.ExitButton.setObjectName(_fromUtf8("ExitButton"))
        self.horizontalLayout.addWidget(self.ExitButton)
        self.horizontalLayout2 = QtGui.QHBoxLayout()

        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Jaundice", "Jaundice", None))
        self.groupBox.setTitle(_translate("Jaundice", "GroupBox", None))
        self.AddButton.setText(_translate("Jaundice", "Test", None))
        self.TextLabel.setText(_translate("Jaundice", "S.Bilirubin Test", None))
        self.TextLabel2.setText(_translate("Jaundice", "S.Bilirubin", None))
        self.TextLabel3.setText(_translate("Jaundice", "Output", None))
        self.ExitButton.setText(_translate("Jaundice", "EXIT", None))
        self.AddButton.clicked.connect(self.add_clicked)
        self.ExitButton.clicked.connect(self.exit_clicked)

    def exit_clicked(self):
        global running
        thd = False
        remove = False
        running = False
        lock = False
        sys.exit(app.exec_())

    def add_clicked(self):
        global captureFrame
        global running
        if running is False:
            running = True
            capture_thread.start()
            self.AddButton.setEnabled(True)
            self.AddButton.setText('Capture')
        else:
            captureFrame=True
            self.AddButton.setEnabled(False)
            self.AddButton.setText('Analysing')


    def update_frame(self):
        global running
        global captureFrame
        global hue
        global ammountOfBilirubin
        if not q.empty():
            if running or captureFrame:
                if captureFrame:
                    self.AddButton.setText('Result')
                    self.TextLabel.setText(str(hue))
                    self.TextLabel2.setText(str(ammountOfBilirubin))
                    if (hue <70):
                        self.TextLabel3.setText('Yes')
                    elif (hue >=70):
                        self.TextLabel3.setText('No')
                frame = q.get()
                img = frame["img"]
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                height, width, bpc = img.shape
                bpl = bpc * width
                image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
                self.ImgWidget.setPixmap(QPixmap(image))

    def closeEvent(self, event):
        global running
        running = False


if __name__ == "__main__":
    capture_thread = threading.Thread(target=grab, args=(1, q))

    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    timer = QTimer()
    timer.timeout.connect(ui.update_frame)
    timer.start(1)
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
