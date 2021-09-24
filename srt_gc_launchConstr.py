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
    gc/srt_gc_launchGui/srt_gc_launchConstr.py

Developers:
    (C) Doddanavar, Roshan    20181205
    (L) Doddanavar, Roshan    2018####

Description:
    <>
    
Input(s):
    <None>
    
Output(s):
    <>
'''

# Installed modules --> Utilities
import sys
import os
import serial
import time
from datetime import datetime
import numpy as np

# Installed modules --> PyQt related
from PyQt5 import QtGui, QtCore, QtSvg
from PyQt5.QtCore import (Qt, QThread, pyqtSignal, QDate, QTime, QDateTime, QSize)
from PyQt5.QtWidgets import (QTextEdit, QLineEdit, QSizePolicy, QFrame, QLabel, QMainWindow, QWidget, QDesktopWidget, QPushButton, QApplication, QGroupBox, QGridLayout, QComboBox)
import pyqtgraph as pg

# Program modules
from srt_gc_launchStyle import Style, Color

class Constr():

    style = Style()
    color = Color()

    pg.setConfigOption('background','w')
    pg.setConfigOption('foreground','k')

    def __init__(self,gui,ledClr):

        self.gui    = gui
        self.ledClr = ledClr

    def image(self,grid,pixmap,pos):

        '''
        Image Constructor Initialization
        '''

        row   = pos[0]
        col   = pos[1]
        rSpan = pos[2]
        cSpan = pos[3]

        image = QLabel()
        image.setAlignment(Qt.AlignCenter)
        image.setPixmap(pixmap)

        grid.addWidget(image,row,col,rSpan,cSpan)

        return image

    def label(self,grid,style,text,align,pos):
        
        '''
        Label Constructor Initialization 
        '''

        # Align must be: "Left", "Center", or "Right" (case-sensitive)

        row   = pos[0]
        col   = pos[1]
        rSpan = pos[2]
        cSpan = pos[3]

        label = QLabel(text)
        label.setAlignment(getattr(Qt,"Align" + align))
        label.setStyleSheet(getattr(self.style.css,style))

        grid.addWidget(label,row,col,rSpan,cSpan)

        return label

    def edit(self,grid,text,pos):
        
        '''
        Line Edit Constructor Initialization
        '''

        row   = pos[0]
        col   = pos[1]
        rSpan = pos[2]
        cSpan = pos[3]

        edit = QLineEdit(text)
        grid.addWidget(edit,row,col,rSpan,cSpan)

        return edit

    def button(self,grid,text,method,color,pos):

        '''
        Button Constructor Initialization
        '''
        
        row   = pos[0]
        col   = pos[1]
        rSpan = pos[2]
        cSpan = pos[3]

        btn = QPushButton(text,self.gui)
        btn.setStyleSheet(self.style.setButton(color))
        btn.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        btn.clicked.connect(getattr(self.gui,method))
        grid.addWidget(btn,row,col,rSpan,cSpan)

        return btn

    def led(self,grid,pos):
        
        '''
        LED Constructor 
        '''

        row   = pos[0]
        col   = pos[1]
        rSpan = pos[2]
        cSpan = pos[3]

        led = QLabel()
        led.setAlignment(Qt.AlignCenter)
        led.setPixmap(self.ledClr.off)
        grid.addWidget(led,row,col,rSpan,cSpan)

        return led

    def readout(self,grid,style,pos):

        '''
        Sensor Readout Constructor
        '''

        row   = pos[0]
        col   = pos[1]
        rSpan = pos[2]
        cSpan = pos[3]

        readout = QLabel()
        readout.setText("-")
        readout.setStyleSheet(getattr(self.style.css,style))
        readout.setAlignment(Qt.AlignCenter)
        readout.setFrameShape(QFrame.StyledPanel)
        readout.setFrameShadow(QFrame.Plain)
        readout.setLineWidth(3)

        grid.addWidget(readout,row,col,rSpan,cSpan)

        return readout

    def plot(self,grid,yRange,xLabel,yLabel,pos):

        '''
        Live Plot Constructor
        '''
        
        row   = pos[0]
        col   = pos[1]
        rSpan = pos[2]
        cSpan = pos[3]

        plot = pg.PlotWidget()

        plot.setFrameShape(QFrame.StyledPanel)
        plot.setFrameShadow(QFrame.Plain)
        plot.showGrid(x=True,y=True,alpha=0.33)

        plot.setYRange(yRange[0],yRange[1])
        plot.setLabel("bottom",xLabel[0],xLabel[1])
        plot.setLabel("left",yLabel[0],yLabel[1])

        grid.addWidget(plot,row,col,rSpan,cSpan)

        return plot

    def scrollBox(self,grid,pos):

        '''
        Scroll Box Constructor 
        '''

        row   = pos[0]
        col   = pos[1]
        rSpan = pos[2]
        cSpan = pos[3]

        scrollBox = QTextEdit()
        scrollBox.setReadOnly(True)
        scrollBox.setLineWrapMode(QTextEdit.NoWrap)
        grid.addWidget(scrollBox,row,col,rSpan,cSpan)

        return scrollBox

    def dropDown(self,grid,pos):

        '''
        Drop Down Constructor 
        '''
        
        row   = pos[0]
        col   = pos[1]
        rSpan = pos[2]
        cSpan = pos[3]

        dropDown = QComboBox(self.gui)
        dropDown.setEditable(True)
        grid.addWidget(dropDown,row,col,rSpan,cSpan)

        return dropDown