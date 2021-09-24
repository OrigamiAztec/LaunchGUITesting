# -*- coding: utf-8 -*-
'''
Texas A&M University Sounding Rocketry Team
SRT-6 | 2018-2019

%-------------------------------------------------------------%
                            TAMU SRT
  _____                      __  _____          __           __
 / ___/______  __ _____  ___/ / / ___/__  ___  / /________  / /
/ (_ / __/ _ \/ // / _ \/ _  / / /__/ _ \/ _ \/ __/ __/ _ \/ / 
\___/_/  \___/\_,_/_//_/\_,_/  \___/\___/_//_/\__/_/  \___/_/  
                                                                      
%-------------------------------------------------------------%

Filepath:
    gc/srt_gc_launchGui/srt_gc_launchThread.py

Developers:
    (C) Doddanavar, Roshan    20181110
    (L) Doddanavar, Roshan    ########

Description:
    <description>
    
Input(s):
    <None>
    
Output(s):
    <None>
'''

# Installed modules --> Utilities
import numpy as np

# Installed modules --> PyQt related
from PyQt5 import (QtGui, QtCore, QtSvg)
from PyQt5.QtCore import (Qt, QThread, pyqtSignal, QDate, QTime, QDateTime, QSize)
from PyQt5.QtWidgets import (QMainWindow, QWidget, QDesktopWidget, QPushButton, QApplication, QGroupBox, QGridLayout)
import pyqtgraph as pg

class UptimeThread(QThread):

    def __init__(self,startGlobal,uptime):

        QThread.__init__(self)

        self.startGlobal = startGlobal
        self.uptime      = uptime 

    def __del__(self):

        self.wait()

    def run(self):

        while (True):

            self.sleep(1)
            elapsed = self.startGlobal.elapsed() 

            # Find stamp digits
            nSec = int(np.floor(elapsed/1000))
            nMin = int(np.floor(nSec/60))
            nHr  = int(np.floor(nMin/60))

            nSec = nSec % 60
            nMin = nMin % 60

            # Generate leading zeros
            if (nSec < 10):
                pSec = '0'
            else:
                pSec = ''

            if (nMin < 10):
                pMin = '0'
            else:
                pMin = ''

            if (nHr < 10):
                pHr = '0'
            else:
                pHr = '' 

            # Update uptime readout
            stamp = pHr + str(nHr) + ':' + pMin + str(nMin) + ':' + pSec + str(nSec)
            self.uptime.setText(stamp)

class PackThread(QThread):

    def __init__(self,packNum):

        QThread.__init__(self)

        self.packNum = packNum

    def __del__(self):

        self.wait()

    def run(self):

        while (True):

            self.sleep(1)
            self.packNum.age += 1

            if (self.packNum.age < 60):
                self.packNum.setText(str(self.packNum.age))
            else:
                self.packNum.setText("60")

class SerThread(QThread):

    outSig   = pyqtSignal(str)
    stateSig = pyqtSignal(str)
    dataSig  = pyqtSignal(str)
    resetSig = pyqtSignal(str)

    def __init__(self,ser):
        
        QThread.__init__(self)

        self.ser = ser

    def __del__(self):

        self.wait()

    def run(self):

        while (True):

            try:
                try:
                    text = self.ser.recv(100)
                except:
                    text = self.ser.readline()
 
                text = text.decode(errors='ignore').strip() # Error catch for encoding issues
                self.outSig.emit(text)

                if (len(text) >= 1): # Crashes if empty string

                    # 'x' prefix for state update
                    if (text[0] == 'x'):
                        self.stateSig.emit(text)

                    # "st" prefix for data packet
                    elif (text[0:2] == "st"):
                        self.dataSig.emit(text)

            except:

                # Emit read fail signal, then wait until thread terminates
                # W/o wait, thread will continuously emit and crash main GUI
                self.resetSig.emit("READ FAIL") 
                self.sleep(5)