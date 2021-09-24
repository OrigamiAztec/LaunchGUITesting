# -*- coding: utf-8 -*-
'''
Texas A&M University Sounding Rocketry Team
SRT-6 | 2018-2019
SRT-9 | 2021-2022

%-------------------------------------------------------------%
                            TAMU SRT
  _____                      __  _____          __           __
 / ___/______  __ _____  ___/ / / ___/__  ___  / /________  / /
/ (_ / __/ _ \/ // / _ \/ _  / / /__/ _ \/ _ \/ __/ __/ _ \/ / 
\___/_/  \___/\_,_/_//_/\_,_/  \___/\___/_//_/\__/_/  \___/_/  
                                                                      
%-------------------------------------------------------------%

Filepath:
    gc/srt_gc_launchGui/srt_gc_launchGui.py

Developers:
    (C) Doddanavar, Roshan    20171216
    (L) Doddanavar, Roshan    20180801
        Diaz, Antonio         

Description:
    Launch Control GUI, interfaces w/ srt_gc_launchArduino/srt_gc_launchArduino.ino
    
Input(s):
    <None>
    
Output(s):
    ./log/*.log    plain-text command log
    ./dat/*.dat    plain-text data archive
'''

# Installed modules --> Utilities
import sys
import os
import serial, serial.tools.list_ports
from serial.serialutil import SerialException
import time
from datetime import datetime
import numpy as np 

# Installed modules --> PyQt related
from PyQt5 import (QtGui, QtCore, QtSvg)
from PyQt5.QtCore import (Qt, QThread, pyqtSignal, QDate, QTime, QDateTime, QSize)
from PyQt5.QtWidgets import (QMainWindow, QWidget, QDesktopWidget, QPushButton, QApplication, QGroupBox, QGridLayout, QStatusBar, QFrame, QTabWidget,QComboBox)
import pyqtgraph as pg

# Program modules
from srt_gc_launchState  import State
from srt_gc_launchThread import SerThread, UptimeThread
from srt_gc_launchTools  import Tools, Object
from srt_gc_launchStyle  import Style, Color
from srt_gc_launchConstr import Constr

# used to monitor wifi networks.
import subprocess

# used to get date and time in clock method.
import datetime as dt

# used to connect to ethernet socket in connect method.
import socket

# data for ethernet connection to SRT6 router
# Create a TCP/IP socket for srt router
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCP_IP = '192.168.1.177'
TCP_PORT = 23
server_address = (TCP_IP, TCP_PORT)

class Gui(QMainWindow):
    
    def __init__(self):

        super().__init__()
        self.initUI()
    
    def initUI(self):      

        '''
        Main Window Initialization
        '''

        # General initialization
        self.session     = '' 
        # current date used in top of window
        self.dateGlobal  = QDate.currentDate()
        # current time used in starting thread time in bottom of window
        self.startGlobal = QTime.currentTime()
        self.version     = "v6.4.0"

        # Container initialization
        self.edit   = Object() # Line edit container
        self.btn    = Object() # Button container
        self.led    = Object() # LED indicator container
        self.ledClr = Object() # LED pixmap container
        self.sensor = Object() # Sensor readout container
        self.data   = Object() # Data array container
        self.plot   = Object() # Plot container

        ledImg = ["green","yellow","red","off"] # LED indicator image files

        for name in ledImg:
            
            # get LED Images in figs folder, green.png, yellow.png, and so on 
            # pixmap = QtGui.QPixmap("./figs/" + name + ".png").scaled(20, 20, 
            pixmap = QtGui.QPixmap("./srt_gc_launchGui/figs/" + name + ".png").scaled(20, 20, 
                     transformMode=QtCore.Qt.SmoothTransformation)

            setattr(self.ledClr,name,pixmap)

        # Utility initialization
        self.style  = Style()
        self.color  = Color()
        self.state  = State(self.led,self.ledClr)
        self.tools  = Tools()
        self.constr = Constr(self,self.ledClr) 

        # Utility states
        self.state.connected = False # Serial connection
        self.state.reading   = False # COM port bypass
        self.state.log       = False # Log/data file initialization 
        self.state.data      = False # Avionics data read

        # Master grid layout management
        self.gridMaster = QGridLayout()
        self.gridMaster.setSpacing(10)

        # Tab initialization
        # name, row, col, row Span, col Span
        tabSpec = [(   "tabComm", 0, 2, 1,  8),
                   (    "tabSys", 1, 0, 1,  2),
                   (     "tabAv", 1, 2, 1,  2),
                   (   "tabFill", 1, 4, 1,  2),
                   (   "tabData", 2, 0, 1, 10)]

        for spec in tabSpec:

            tabName = spec[0]
            row     = spec[1]
            col     = spec[2]
            rSpan   = spec[3]
            cSpan   = spec[4]

            tab = QTabWidget()
            setattr(self,tabName,tab)
            self.gridMaster.addWidget(tab,row,col,rSpan,cSpan)

        # kind, grid, title, row, col, row Span, col Span
        groupSpec = [( "box",  "groupTitle",  "gridTitle",                            "", 0, 0, 1,  2),
                     ( "tab", "groupComm", "gridComm",               "Communication",   "tabComm"),
                     ( "tab", "groupSess", "gridSess",             "Session Control",   "tabComm"),
                     ( "tab",  "groupSys",  "gridSys",                "System State",    "tabSys"),
                     ( "tab",  "groupPwr",  "gridPwr",             "Power Telemetry",    "tabSys"),
                     ( "tab",  "groupDaq",  "gridDaq",                "Avionics DAQ",     "tabAv"),  
                     ( "tab", "groupDiag", "gridDiag",                 "Diagnostics",     "tabAv"),
                     ( "tab", "groupFill", "gridFill",                "Fill Control",   "tabFill"),
                     ( "tab", "groupAuto", "gridAuto",                   "Auto Fill",   "tabFill"),
                     ( "box",  "groupIgn",  "gridIgn",             "Igniter Control", 1, 6, 1,  2),  
                     ( "box",  "groupVal",  "gridVal",               "Valve Control", 1, 8, 1,  2),
                     ( "tab", "groupPlot", "gridPlot",          "Engine Diagnostics",   "tabData"),
                     ( "tab",  "groupOut",  "gridOut",               "Serial Output",   "tabData"),]

        for spec in groupSpec:

            kind      = spec[0]
            groupName = spec[1]
            gridName  = spec[2]
            title     = spec[3]

            if (kind == "tab"):

                parent = spec[4]
                group  = QWidget()
                grid   = QGridLayout()

                # Widget initialization
                setattr(self,groupName,group)

                # GridLayout object initialization
                setattr(self,gridName,grid)
                group.setLayout(grid)
                group.setAutoFillBackground(True)

                # Tab assignment
                getattr(self,parent).addTab(group,title)

            elif (kind == "box"):

                row       = spec[4]
                col       = spec[5]
                rSpan     = spec[6]
                cSpan     = spec[7]

                # GroupBox object initialization
                group = QGroupBox(title)
                group.setStyleSheet(self.style.css.group)

                # GridLayout object initialization
                grid = QGridLayout()
                group.setLayout(grid)

                # Assign to parent objects
                setattr(self,gridName,grid)
                setattr(self,groupName,group)
                self.gridMaster.addWidget(group,row,col,rSpan,cSpan)

        # Call initialization routines
        self.titleInit()   # Title bar  
        self.barInit()     # Bottom statusbar
        self.commInit()    # Communication toolbar
        self.sessInit()    # Session toolbar 
        self.btnCtrlInit() # Buttons for control panel 
        self.ledCtrlInit() # LED inidicators " "
        self.plotInit()    # Engine diagnostics, plots
        self.dataInit()    # Engine diagnostics, readouts
        self.outInit()     # Raw serial output
        
        # Row & column stretching in master grid
        rowStr = [1, 4, 8]
        colStr = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        self.tools.resize(self.gridMaster,rowStr,colStr)

        # Finalize widget
        mainWidget = QWidget()
        mainWidget.setLayout(self.gridMaster)
        self.setCentralWidget(mainWidget)

        # Window management 
        self.setWindowTitle("SRT Ground Control " + self.version + " " + self.dateGlobal.toString(Qt.TextDate))
        self.setWindowIcon(QtGui.QIcon("./figs/desktop_icon.png"))
        self.showMaximized() 

        # Window centering
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Window formatting
        #self.setStyleSheet(self.style.css.window)

        # Final initialization
        self.show()

    def titleInit(self): 

        '''
        Window Title Initialization
        '''

        # QLabel --> SRT logo
        #titImg = "./figs/srt_black.svg"
        titImg = "./srt_gc_launchGui/figs/srt_black.svg"
        pixmap = QtGui.QPixmap(titImg).scaled(50,50,transformMode=QtCore.Qt.SmoothTransformation)
        self.logo = self.constr.image(self.gridTitle,pixmap,[0,0,2,1])

        # QLabel --> Main window title 
        text = "SRT Ground Control" + " " + self.version
        self.title = self.constr.label(self.gridTitle,"title",text,"Bottom",[0,1,1,1])

        # QLabel --> Main window subtitle
        text = "Remote Launch System [tamusrt/gc]"
        self.subtitle = self.constr.label(self.gridTitle,"subtitle",text,"Top",[1,1,1,1])

        # Row & column stretching in title grid
        rowStr = [5, 1]
        colStr = [1, 2]

        self.tools.resize(self.gridTitle,rowStr,colStr)

    def barInit(self):

        '''
        Initialize strings and inputs in bottom status bar.
        '''

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
 
        barFrame   = QFrame()
        gridStatus = QGridLayout()
        barFrame.setLayout(gridStatus)
        self.statusBar.addPermanentWidget(barFrame,1)

        # Event log
        self.constr.label(gridStatus,"label","EVENT LOG","Center",[0,0,1,1])
        self.statusBar.log = self.constr.readout(gridStatus,"statusBar",[0,1,1,1])

        # Last sent
        self.constr.label(gridStatus,"label","LAST SENT","Center",[0,2,1,1])
        self.statusBar.sent = self.constr.readout(gridStatus,"statusBar",[0,3,1,1])

        # Last recieved
        self.constr.label(gridStatus,"label","LAST RCVD","Center",[0,4,1,1])
        self.statusBar.recieved = self.constr.readout(gridStatus,"statusBar",[0,5,1,1])

        # Session name
        self.constr.label(gridStatus,"label","SESSION","Center",[0,6,1,1])
        self.statusBar.session = self.constr.readout(gridStatus,"statusBar",[0,7,1,1])

        # Uptime counter
        self.constr.label(gridStatus,"label","UPTIME","Center",[0,8,1,1])
        self.statusBar.uptime = self.constr.readout(gridStatus,"statusBar",[0,9,1,1])

        # Uptime thread management
        self.uptimeThread = UptimeThread(self.startGlobal,self.statusBar.uptime)
        self.uptimeThread.start()

        # Row & column stretching in comm grid
        rowStr = [] 
        colStr = [1, 4, 1, 2, 1, 2, 1, 2, 1, 2]

        self.tools.resize(gridStatus,rowStr,colStr)

    def commInit(self):

        '''
        Communication Toolbar Initialization
        '''

        # set communication and reading status as false initially.
        self.state.connected = False
        self.state.reading   = False

        if (os.name == "posix"):
            prefix = "/dev/tty"
        elif (os.name == "nt"):
            prefix = "COM"
        else: 
            prefix = ""

        # LED indicator for connection
        self.led.commConn = self.constr.led(self.gridComm,[0,0,1,1])

        # CONNECT button
        method = "btnClkConn"
        color  = self.color.comm
        self.btn.commConn = self.constr.button(self.gridComm,"CONNECT",method,color,[0,1,1,1])

        # SEARCH button 
        method = "btnClkSearch"
        color  = self.color.comm
        self.btn.commSearch = self.constr.button(self.gridComm,"SEARCH",method,color,[0,2,1,1])

        # COM Port label & input
        self.labPort  = self.constr.label(self.gridComm,"label","Data Port:","Center",[0,3,1,1])
        self.portMenu = self.constr.dropDown(self.gridComm,[0,4,1,1])

        # Baud rate label & input
        self.labBaud   = self.constr.label(self.gridComm,"label","Baud Rate","Center",[0,5,1,1])
        self.baudMenu  = self.constr.dropDown(self.gridComm,[0,6,1,1])
        self.baudMenu.addItems(["9600","14400","19200","28800","38400","57600","115200"])

        # LED indicator for bypass
        self.led.commByp = self.constr.led(self.gridComm,[0,7,1,1])

        # BYPASS button. Function of bypass is to force GUI to send commands over xbee even if xbee port isn't showing.
        method = "btnClkByp"
        color  = self.color.comm
        self.btn.commByp = self.constr.button(self.gridComm,"BYPASS",method,color,[0,8,1,1])

        # RESET button. Function of reset is to stop thread sorting, turn off all LEDs and disconnect xbees. May want to add more functionality such as returning to a safe state of the engine.
        method = "btnClkRes"
        color  = self.color.comm
        self.btn.commRes = self.constr.button(self.gridComm,"RESET",method,color,[0,9,1,1])

        # Row & column stretching in comm grid
        rowStr = [] 
        colStr = [1, 3, 3, 2, 5, 2, 2, 1, 3, 3]

        self.tools.resize(self.gridComm,rowStr,colStr)

    def sessInit(self):

        # Session name
        self.led.sess       = self.constr.led(self.gridSess,[0,0,1,1])
        self.btn.sessNew    = self.constr.button(self.gridSess,"NEW","btnClkSessNew",self.color.comm,[0,1,1,1])
        self.btn.sessRename = self.constr.button(self.gridSess,"RENAME","btnClkSessRename",self.color.comm,[0,2,1,1])
        self.labSess        = self.constr.label(self.gridSess,"label","Session","Center",[0,3,1,1])
        self.edit.session   = self.constr.edit(self.gridSess,"test",[0,4,1,1])

        # Clock control
        self.led.clock      = self.constr.led(self.gridSess,[0,5,1,1])
        self.btn.sessClock  = self.constr.button(self.gridSess,"SET CLOCK","btnClkClock",self.color.comm,[0,6,1,1])

        self.labDateYr      = self.constr.label(self.gridSess,"label","Date","Center",[0,7,1,1])
    
        self.edit.dateYYYY  = self.constr.edit(self.gridSess,"YYYY",[0,8,1,1])
        self.edit.dateMM    = self.constr.edit(self.gridSess,"MM",[0,9,1,1])
        self.edit.dateDD    = self.constr.edit(self.gridSess,"DD",[0,10,1,1])

        self.labTime        = self.constr.label(self.gridSess,"label","Time","Center",[0,11,1,1])
        self.edit.timeHH    = self.constr.edit(self.gridSess,"HH",[0,12,1,1])
        self.edit.timeMM    = self.constr.edit(self.gridSess,"MM",[0,13,1,1])
        self.edit.timeSS    = self.constr.edit(self.gridSess,"SS",[0,14,1,1])

        # Row & column stretching in sess grid
        rowStr = [] 
        colStr = [1, 2, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1]

        self.tools.resize(self.gridSess,rowStr,colStr)

    def btnClkSearch(self):
        # set the port menu to be cleared initially.
        self.portMenu.clear()

        # check the number of serial ports available.
        ports = serial.tools.list_ports.comports()

        # if ports exist, add it to drop down menu in GUI
        if (ports):
            for port in ports:
                entry = "Serial: " + port.device + " - " + port.description
                self.portMenu.addItem(entry)
        
        # uses subprocess package to check for connected wifi networks.
        devices = subprocess.check_output(['netsh','wlan','show','network']).decode('ascii').replace("\r","")
        numOfWifiDevices = len(devices.split("SSID"))
        
        #  check to see the number of wifi networks we can connect to 
        if numOfWifiDevices:
            for deviceNum in range(1, numOfWifiDevices):
                entry = "Wifi Network: " + devices.split("SSID")[deviceNum].split(" ")[3]
                self.portMenu.addItem(entry)

        else:
            self.portMenu.setCurrentText("NO DEVICE(S) FOUND")

    def btnClkClock(self):
        '''
        "CLOCK" Button Event Handling 
        '''

        # probably better to replace these with QDate class to reduce number of packages you have to import.
        year = str(dt.datetime.now().year)
        month = str(dt.datetime.now().month)
        day = str(dt.datetime.now().day)

        hour = str(datetime.now().hour)
        minute = str(dt.datetime.now().minute)
        seconds = str(dt.datetime.now().second)

        # automatically update date and time log when button clicked
        self.edit.dateYYYY  = self.constr.edit(self.gridSess,year,[0,8,1,1])
        self.edit.dateMM    = self.constr.edit(self.gridSess,month,[0,9,1,1])
        self.edit.dateDD    = self.constr.edit(self.gridSess,day,[0,10,1,1])

        self.edit.timeHH    = self.constr.edit(self.gridSess,hour,[0,12,1,1])
        self.edit.timeMM    = self.constr.edit(self.gridSess,minute,[0,13,1,1])
        self.edit.timeSS    = self.constr.edit(self.gridSess,seconds,[0,14,1,1])

        # I think this was meant to pull up exact date and time on a separate window for user to type in manually.
        # This command below with os.system doesn't work. sudo command not recognized on windows.
        # dateStr = self.edit.dateYYYY.text() + '-' + self.edit.dateMM.text() + '-' + self.edit.dateDD.text()
        # timeStr = self.edit.timeHH.text() + ':' + self.edit.timeMM.text() + ':' + self.edit.timeSS.text()
        # cmdStr  = "sudo date -s"
        # System command
        # sudo date -s 'YYYY-MM-DD HH:MM:SS'
        #os.system('cmdStr' + ' ' + '\'' + dateStr + ' ' + timeStr + '\'')

        self.led.clock.setPixmap(self.ledClr.yellow)


    def btnClkConn(self):

        '''
        "CONNECT" Button Event Handling. Attempts to connect to SRT Router and Serial
        '''

        if (self.state.connected):
            self.logEvent("ERROR","ALREADY CONNECTED")
        else: 

            # User input --> Port name & baud rate
            text      = str(self.portMenu.currentText())
            text      = text.split(' ')
            self.port = text[0]
            self.baud = int(str(self.baudMenu.currentText()))

            if (self.port == "/dev/tty"):
                self.logEvent("ERROR","INVALID PORT")
            else:
                if (self.port == "Wifi"):
                    try:
                        # Attempt to connect to router/ethernet over ubiquity
                        sock.connect(server_address)
                        self.ser = sock

                        # Set connected Status true, change LED, log connected status if connected to Ethernet
                        self.state.connected = True
                        self.logEvent("CONNECTED",self.port)                    
                        self.led.commConn.setPixmap(self.ledClr.yellow)

                        # must send a command initially for it to stay connected and read data over ethernet.
                        missionCMD = 'b'
                        missionCMD = bytes(missionCMD, 'utf-8')
                        sock.sendall(missionCMD)

                        # Thread handling
                        self.serThread  = SerThread(self.ser)

                        self.serThread.outSig.connect(self.outUpdate)
                        self.serThread.stateSig.connect(self.stateUpdate)
                        self.serThread.dataSig.connect(self.dataUpdate)
                        self.serThread.resetSig.connect(self.readFail)
                        
                        # Test for bypass condition
                        text = self.ser.recv(100)
                        if (len(text) > 0):

                            # Check for empty packet
                            self.state.reading = True
                            self.logEvent("READING",self.port)
                            self.led.commByp.setPixmap(self.ledClr.yellow)

                            self.serThread.start()
                    except (TimeoutError, OSError):
                        self.logEvent("ERROR","INVALID PORT") 
                else:
                    try:
                        # Attempt to connect to serial
                        self.ser = serial.Serial(self.port,self.baud,timeout=1)
                        self.state.connected = True
                        self.logEvent("CONNECTED",self.port)                    
                        self.led.commConn.setPixmap(self.ledClr.yellow)

                        # trying to send a command initially to see if that makes it easy to get connected.
                        missionCMD = 'b'
                        missionCMD = bytes(missionCMD, 'utf-8')
                        self.ser.write(missionCMD)
                
                        # Thread handling
                        self.serThread  = SerThread(self.ser)

                        self.serThread.outSig.connect(self.outUpdate)
                        self.serThread.stateSig.connect(self.stateUpdate)
                        self.serThread.dataSig.connect(self.dataUpdate)
                        self.serThread.resetSig.connect(self.readFail)

                        # Test for bypass condition
                        text = self.ser.readline()

                        if (len(text) > 0):

                            # Check for empty packet
                            self.state.reading = True
                            self.logEvent("READING",self.port)
                            self.led.commByp.setPixmap(self.ledClr.yellow)
    
                            self.serThread.start()
                    except:
                        self.logEvent("ERROR","INVALID PORT") 
               

    def btnClkByp(self):
        # haven't updated bypass method for ubiquity, just Xbee
        '''
        "BYPASS" Button Event Handling --> XBee (old) firmware quirk
        '''

        if (self.state.reading):
            self.logEvent("ERROR","ALREADY READING")
        elif (not self.state.connected):
            self.logEvent("ERROR","NO CONNECTION")
        else:

            # enter, enter, (wait), 'b' --> bypass XBee dongle w/ ascii encoding 
            self.ser.write(b'\r\n\r\n')
            time.sleep(2)
            self.ser.write(b'b\r\n')

            # Test for bypass condition
            text = self.ser.readline()

            if (len(text) > 0):

                # Check for empty packet
                self.state.reading = True
                self.logEvent("READING",self.port)
                self.led.commByp.setPixmap(self.ledClr.yellow)

                self.serThread.start()
            
    def btnClkRes(self):

        '''
        "RESET" Button Event Handling
        '''

        if (self.state.connected):

            # This is discouraged but thread.quit() and thread.exit() don't work [brute force method]
            self.serThread.terminate()
            self.state.reading = False
            self.led.commByp.setPixmap(self.ledClr.off)

            self.ser.close()
            self.state.connected = False 
            self.logEvent("DISCONNECTED",self.port)
            self.led.commConn.setPixmap(self.ledClr.off)

            # Reset all control status LEDs
            ledName = list(self.led.__dict__)

            for name in ledName:
                if (name == "sess"): # Don't reset session LED
                    continue
                else:
                    getattr(self.led,name).setPixmap(self.ledClr.off)

        else:
            self.logEvent("ERROR","NO CONNECTION")
        
    def btnCtrlInit(self):  

        '''
        Control Button Initialization
        '''

        rSp = 1 # Row span multiplier
        cSp = 2 # Column span mutilplier

        # Control button specification
        # grid, name, text, comm, color, row, col, row span, col span

        # System state
        btnSpec = [(  "gridSys",        "sysArm",         "SYS ARM",       "btnClkCtrl",  "sys", 0, 0, 1, 1),
                   (  "gridSys",     "sysDisarm",      "SYS DISARM",       "btnClkCtrl",  "sys", 0, 1, 1, 1),
                   (  "gridSys",        "ready1",         "READY 1",       "btnClkCtrl",  "abt", 1, 0, 1, 1),
                   (  "gridSys",        "ready2",         "READY 2",       "btnClkCtrl",  "abt", 2, 0, 1, 1),  
                   (  "gridSys",         "abort",           "ABORT",       "btnClkCtrl",  "abt", 1, 1, 2, 1),
                   (  "gridSys",        "buzzOn",         "BUZZ ON",       "btnClkCtrl",  "sys", 3, 0, 1, 1),  
                   (  "gridSys",       "buzzOff",        "BUZZ OFF",       "btnClkCtrl",  "sys", 3, 1, 1, 1),
        # Data acquisition
                   (  "gridDaq",     "dataState",      "DATA STATE",       "btnClkCtrl",  "daq", 0, 0, 1, 1),
                   (  "gridDaq",      "avPwrOff",      "AV PWR OFF",       "btnClkCtrl",   "av", 0, 1, 1, 1),
                   (  "gridDaq",     "dataStart",      "DATA START",       "btnClkCtrl",  "daq", 1, 0, 1, 1),
                   (  "gridDaq",      "dataStop",       "DATA STOP",       "btnClkCtrl",  "daq", 1, 1, 1, 1),
        # Fill control
                   ( "gridFill",    "supplyOpen",     "SUPPLY OPEN",       "btnClkCtrl",  "n2o", 0, 0, 1, 1),
                   ( "gridFill",   "supplyClose",    "SUPPLY CLOSE",       "btnClkCtrl",  "n2o", 0, 1, 1, 1),
                   ( "gridFill",  "supplyVtOpen",  "SUPPLY VT OPEN",       "btnClkCtrl",  "n2o", 1, 0, 1, 1),
                   ( "gridFill", "supplyVtClose", "SUPPLY VT CLOSE",       "btnClkCtrl",  "n2o", 1, 1, 1, 1),
                   ( "gridFill",     "runVtOpen",     "RUN VT OPEN",       "btnClkCtrl",  "n2o", 2, 0, 1, 1),
                   ( "gridFill",    "runVtClose",    "RUN VT CLOSE",       "btnClkCtrl",  "n2o", 2, 1, 1, 1),
                   ( "gridFill",       "motorOn",        "MOTOR ON",       "btnClkCtrl",   "qd", 3, 0, 1, 1),
                   ( "gridFill",      "motorOff",       "MOTOR OFF",       "btnClkCtrl",   "qd", 3, 1, 1, 1),
        # Igniter control
                   (  "gridIgn",       "ignCont",        "IGN CONT",       "btnClkCtrl",  "ign", 0, 0, 1, 2),
                   (  "gridIgn",        "ignArm",         "IGN ARM",       "btnClkCtrl",  "ign", 1, 0, 1, 1),
                   (  "gridIgn",     "ignDisarm",      "IGN DISARM",       "btnClkCtrl",  "ign", 1, 1, 1, 1),
                   (  "gridIgn",        "oxOpen",         "OX OPEN",       "btnClkCtrl",   "o2", 2, 0, 1, 1),
                   (  "gridIgn",       "oxClose",        "OX CLOSE",       "btnClkCtrl",   "o2", 2, 1, 1, 1),
                   (  "gridIgn",         "ignOn",          "IGN ON",       "btnClkCtrl",  "ign", 3, 0, 1, 1),
                   (  "gridIgn",        "ignOff",         "IGN OFF",       "btnClkCtrl",  "ign", 3, 1, 1, 1),
        # Valve control
                   (  "gridVal",       "bvPwrOn",       "BV PWR ON",       "btnClkCtrl", "bvas", 0, 0, 1, 1),
                   (  "gridVal",      "bvPwrOff",      "BV PWR OFF",       "btnClkCtrl", "bvas", 0, 1, 1, 1),
                   (  "gridVal",        "bvOpen",         "BV OPEN",       "btnClkCtrl", "bvas", 1, 0, 1, 1),
                   (  "gridVal",       "bvClose",        "BV CLOSE",       "btnClkCtrl", "bvas", 1, 1, 1, 1),
                   (  "gridVal",       "bvState",        "BV STATE",       "btnClkCtrl", "bvas", 2, 0, 1, 1),
                   (  "gridVal",          "mdot",            "MDOT",       "btnClkCtrl", "mdot", 2, 1, 1, 1)]  

        for spec in btnSpec:
            
            grid   = getattr(self,spec[0])
            name   = spec[1]
            text   = spec[2]
            method = spec[3]
            color  = getattr(self.color,spec[4])

            row    = spec[5]*rSp
            col    = spec[6]*cSp           
            rSpan  = spec[7]*rSp
            cSpan  = spec[8]*cSp
            
            # Construct button 
            btn      = self.constr.button(grid,text,method,color,[row,col,rSpan,cSpan])
            btn.comm = self.state.btnMap(name) # Find & set character command
            btn.led  = [] # Create empty list of associated LEDs

            # Assign to container
            setattr(self.btn,name,btn)
            
    def btnClkCtrl(self):

        '''
        Control Button Event Handling
        '''
      
        sender = self.sender()
        self.statusBar.sent.setText(sender.text()) # Update statusbar
        self.logEvent(sender.text(),sender.comm)   

        # Trigger red LED state
        if (self.state.connected):
            for led in sender.led:
                led.setPixmap(self.ledClr.red)

        try:

            comm = sender.comm.encode("ascii")
            try:
                self.ser.sendall(comm)
            except:
                self.ser.write(comm)

        except: 

            if (self.state.connected):
                self.logEvent("ERROR","WRITE FAIL")
            else:
                self.logEvent("ERROR","NO CONNECTION")

    def btnClkSessRename(self):

        if (self.state.log):
            
            self.session = self.edit.session.text()
            self.statusBar.session.setText(self.session)

        else:
            self.logEvent("ERROR","FILE IO")

    def btnClkSessNew(self):
        
        try: 

            # Close log & data files if initialized
            self.closeLog()

            # Update session name
            self.session = self.edit.session.text()
            self.statusBar.session.setText(self.session)

            # Generate file date & time stamp(s)
            dateLocal  = QDate.currentDate()
            dateStr    = dateLocal.toString(Qt.ISODate)

            startLocal = QTime.currentTime()
            startStr   = startLocal.toString("HH:mm:ss")

            # Control & data log initialization
            fileObj = ["logFile","dataFile"]
            fileDir = ["./log/","./data/"] 
            fileExt = [".log",".dat"]

            for i in range(len(fileObj)):
                
                fileName = dateStr.replace('-','') + '_' + startStr.replace(':','') + fileExt[i]

                if (not os.path.exists(fileDir[i])):
                    os.makedirs(fileDir[i])

                setattr(self,fileObj[i],open(fileDir[i] + fileName,'w'))

            self.state.log = True
            self.led.sess.setPixmap(self.ledClr.yellow)

        except:
            self.logEvent("ERROR","FILE IO")

    def ledCtrlInit(self): 

        '''
        LED Inidicator Initialization
        '''

        rSp = 1 # Row span multiplier
        cSp = 2 # Column span multiplier

        # LED indicator specification 
        # grid, name, row, col, row Span, col Span, buttons ...

        # System state
        ledSpec = [(  "gridSys",   "sysArm", 0, 2, 1, 1,       "sysArm",     "sysDisarm"), 
                   (  "gridSys",   "ready1", 1, 2, 1, 1,       "ready1",         "abort"),
                   (  "gridSys",   "ready2", 2, 2, 1, 1,       "ready2",         "abort"), 
                   (  "gridSys",     "buzz", 3, 2, 1, 1,       "buzzOn",       "buzzOff"), 
        # Data acquisition 
                   (  "gridDaq",    "avPwr", 0, 2, 1, 1,     "avPwrOff"),               
                   (  "gridDaq",     "data", 1, 2, 1, 1,    "dataStart",      "dataStop", "dataState"),      
        # Fill control
                   ( "gridFill",   "supply", 0, 2, 1, 1,   "supplyOpen",   "supplyClose"),     
                   ( "gridFill", "supplyVt", 1, 2, 1, 1, "supplyVtOpen", "supplyVtClose"), 
                   ( "gridFill",    "runVt", 2, 2, 1, 1,    "runVtOpen",    "runVtClose"), 
                   ( "gridFill",    "motor", 3, 2, 1, 1,      "motorOn",      "motorOff"), 
        # Igniter control
                   (  "gridIgn",  "ignCont", 0, 2, 1, 1,      "ignCont"), 
                   (  "gridIgn",   "ignArm", 1, 2, 1, 1,       "ignArm",     "ignDisarm"), 
                   (  "gridIgn",       "ox", 2, 2, 1, 1,       "oxOpen",       "oxClose"), 
                   (  "gridIgn",      "ign", 3, 2, 1, 1,        "ignOn",        "ignOff"), 
        # Valve control
                   (  "gridVal",    "bvPwr", 0, 2, 1, 1,      "bvPwrOn",      "bvPwrOff",   "bvState", "mdot"),
                   (  "gridVal",       "bv", 1, 2, 1, 1,       "bvOpen",       "bvClose",   "bvState", "mdot")]

        for spec in ledSpec:
            
            grid  = getattr(self,spec[0])
            name  = spec[1]
            row   = spec[2]*rSp
            col   = spec[3]*cSp           
            rSpan = spec[4]*rSp
            cSpan = spec[5]*cSp/2
            btn   = spec[6:]

            # Construct LED 
            led = self.constr.led(grid,[row,col,rSpan,cSpan])

            # Attach LEDs to associated buttons
            for btnName in btn:
                getattr(self.btn,btnName).led.append(led)

            # Assign to container
            setattr(self.led,name,led)

    def dataInit(self): 

        '''
        Data Array & Sensor Readout Initialization
        '''

        # Data storage initialization
        # time stamp, run tank press, chamber press, run tank temp, chamber temp, aux temp
        self.dataTime = 1*60 # Data array length (sec)
        self.dataName = ["st","pt","pc","tt","tc","ta"]
        self.dataDict = {}

        for name in self.dataName:
            # looks like it sets dataDict[st], dataDict[pt], ... and so on to none in initialization
            setattr(self.data,name,np.array([]))
            self.dataDict[name] = None

        # Sensor readout specification
        # name, text, unit, code, row, col, row span, col span

        # Pressure column
        sensorSpec = [(    "pRun",       "Press\nRun", "[ psi ]", "pt",    0, 0, 2, 1, 1),
                      ( "pRun30s",   "Extrap\n30 sec", "[ psi ]", "pt",   30, 1, 2, 1, 1),
                      (  "pRun1m",    "Extrap\n1 min", "[ psi ]", "pt", 1*60, 2, 2, 1, 1),
                      (  "pRun5m",    "Extrap\n5 min", "[ psi ]", "pt", 5*60, 3, 2, 1, 1),
                      (  "pChamb",     "Press\nChamb", "[ psi ]", "pc",    0, 4, 2, 1, 1),
        # Temperature column
                      (    "tRun",        "Temp\nRun",  "[ °F ]", "tt",    0, 0, 6, 1, 1),
                      ( "tRun30s",   "Extrap\n30 sec",  "[ °F ]", "tt",   30, 1, 6, 1, 1),
                      (  "tRun1m",    "Extrap\n1 min",  "[ °F ]", "tt", 1*60, 2, 6, 1, 1),
                      (  "tRun5m",    "Extrap\n5 min",  "[ °F ]", "tt", 5*60, 3, 6, 1, 1),
                      ( "pRunVap",     "Press\nVapor", "[ psi ]", "tt",    0, 4, 6, 1, 1)]

        for spec in sensorSpec:

            name   = spec[0]
            text   = spec[1]
            unit   = spec[2]
            code   = spec[3]
            extrap = spec[4]
            
            row    = spec[5]
            col    = spec[6]
            rSpan  = spec[7]
            cSpan  = spec[8]

            # Construct sensor & assign to container 
            sensor        = self.constr.readout(self.gridPlot,"sensor",[row,col,rSpan,cSpan])
            sensor.code   = code   # Data code
            sensor.extrap = extrap # Forward extrapolation time

            # Assign to container
            setattr(self.sensor,name,sensor)

            # Sensor text & unit labels 
            self.constr.label(self.gridPlot,"label",text,"Center",[row,col-1,1,1])
            self.constr.label(self.gridPlot,"label",unit,"Center",[row,col+1,1,1])

        # Generate sensor list
        self.sensorName = list(self.sensor.__dict__)

        # Row & column stretching in plotGrid
        rowStr = []
        colStr = [8, 1, 1, 1, 8, 1, 1, 1]

        self.tools.resize(self.gridPlot,rowStr,colStr)

    def plotInit(self): 

            '''
            Live Plot Initialization
            '''

            self.plot = [None] * 2

            # Pressure plot
            yRange = [0,950]
            xLabel = ["Time","sec"]
            yLabel = ["Run Tank Pressure","psi"]
            hour = [1,2,3,4,5,6,7,8,9,10]
            temperature = [400,432,434,432,433,431,429,432,435,445]

            self.plot[0]   = self.constr.plot(self.gridPlot,yRange,xLabel,yLabel,[0,0,5,1])
            self.plotPress = self.plot[0].plot()
            
            # Temperature plot 
            yRange = [0,150]
            xLabel = ["Time","sec"]
            yLabel = ["Run Tank Temperature","°F"]
            hour = [1,2,3,4,5,6,7,8,9,10]
            temperature = [100,90,80,90,90,90,100,100,100,100]

            self.plot[1]  = self.constr.plot(self.gridPlot,yRange,xLabel,yLabel,[0,4,5,1])
            self.plotTemp = self.plot[1].plot()

    def outInit(self):

        # Create scroll box for raw serial output 
        self.serialOut = self.constr.scrollBox(self.gridOut,[0,0,1,1])

    def outUpdate(self,text):

        self.serialOut.moveCursor(QtGui.QTextCursor.End)
        self.serialOut.insertPlainText(text + "\n")
        sb = self.serialOut.verticalScrollBar()
        sb.setValue(sb.maximum())

    def stateUpdate(self,text):
        '''
        Control State Update
        '''

        # Update statusbar
        self.statusBar.recieved.setText(text)

        try:

            # Logs state event, update state object, update PID graphic (eventually)
            self.logEvent("STATE",text)

            # QUICK FIX FOR ABORT STATE 
            if (text == "xLBabo"):
                self.state.update("xLBrl10")
                self.state.update("xLBrl20")
            else:
                self.state.update(text)

        except:
            self.logEvent("ERROR","STATE FAIL")

    def dataUpdate(self,text): 
        print("gets here, right?")
        '''
        Plot & Sensor Update
        '''

        try: 

            # Write to data log
            if self.state.log:
                self.dataFile.write(text + '\n')
                print("writing")

            # Process data packet
            raw  = text.split(',')
            nEnd = len(self.data.st)
            print(raw, nEnd)

            # Update dictionary --> maps code to reading
            for field in raw:
                self.dataDict[field[0:2]] = field[2:]

            # Convert time stamps to elapsed from AV start (first packet)
            if (self.state.data):

                stamp   = self.dataDict["st"]
                nowData = datetime.strptime(stamp,"%H:%M:%S.%f")
                delta   = nowData - self.startData
                elapsed = delta.total_seconds()

                self.dataDict["st"] = elapsed

            else:
                
                stamp           = self.dataDict["st"]
                self.startData  = datetime.strptime(stamp,"%H:%M:%S.%f")
                self.state.data = True

                self.dataDict["st"] = 0

            # Establish extrapolation time step
            if (len(self.data.st) < 2):
                step = 1 # Arbitrary value; can't be zero
            else:
                step = self.data.st[-1] - self.data.st[-2]

            nData = np.floor(self.dataTime/step)

            # Populate data arrays: after filling array, delete first element & append to end
            if (nEnd < nData): # Case: array not full

                for name in self.dataName:

                    value = float(self.dataDict[name])
                    setattr(self.data,name,np.append(getattr(self.data,name),value))

            else: # Case: array full

                for name in self.dataName:

                    value = float(self.dataDict[name])
                    getattr(self.data,name,np.roll(getattr(self.data,name),-1))
                    getattr(self.data,name)[-1] = value

            # Sensor readout update
            for name in self.sensorName:

                sensor = getattr(self.sensor,name)
                data   = getattr(self.data,sensor.code)
                value  = self.tools.extrap(self.data.st,data,sensor.extrap,step)

                if (name == "pRunVap"): # Vapor pressure from run tank temp
                    value = self.tools.vapPress(value)

                sensor.setText(str(round(value,2)))

            # Live plot update
            #xTime  = self.data.st - self.data.st[-1] # Center time scale at present reading 
            xTime = [1,2,3,4,5,6,7,8,9,10]
            yPress = [400,432,434,432,433,431,429,432,435,445]
            print(xTime)
            print("YPress:")
            print(yPress)
            #yPress = self.data.pt # Tank pressure array
            yTemp  = self.data.tt # Tank temperature array 
            print("yTemp:")
            print(yTemp)

            self.plotPress.setData(xTime,yPress,pen=self.style.pen.press)
            self.plotTemp.setData(xTime,yTemp,pen=self.style.pen.temp)

        except: 

            # Throws error if failure to read data packet
            self.logEvent("ERROR","DAQ FAIL")

            if (self.state.log):
                self.dataFile.write("ERROR: " + text + '\n')
                
    def readFail(self,text):

        '''
        Log Read Fail & Reset Connection
        '''

        self.btnClkRes()
        self.logEvent("ERROR",text)

    def logEvent(self,event,text): 
        
        '''
        Log Event Management 
        '''

        # Build, print stamp to statusbar & log
        now   = QTime.currentTime()
        stamp = now.toString("HH:mm:ss.zzz")
        pad   = ' ' * 5

        # Print to statusbar, format if necessary
        self.statusBar.log.setText(stamp + pad + event + pad + "\"" + text + "\"")

        if (event == "ERROR"):
            self.statusBar.log.setStyleSheet(self.style.css.error)
        else: 
            self.statusBar.log.setStyleSheet(self.style.css.statusBar)

        # Print to log file
        if (self.state.log):
            self.logFile.write(stamp + ", " + event + ", " + "\"" + text + "\"" + "\n")

    def closeLog(self):

        '''
        File Close Management
        '''

        if (self.state.log):

            self.state.log = False # Protects thread issues; writing to closed file
            fileObj = ["logFile","dataFile"]

            for logName in fileObj:

            # Close & rename file(s)
                filePath    = getattr(self,logName).name.split('/')
                filePath[2] = self.session + '_' + filePath[2]
                filePath    = '/'.join(filePath)

                getattr(self,logName).close()
                os.rename(getattr(self,logName).name,filePath)

    def closeEvent(self,event):
        
        '''
        GUI Exit Management
        '''

        # Close log & data files if initialized
        self.closeLog()

        # Exit GUI safely
        event.accept()
        
if (__name__ == '__main__'):
    
    '''
    Executive Control
    '''

    app = QApplication(sys.argv) # Utility for window exit condition
    gui = Gui()                  # Creates instance of "Gui" class
    sys.exit(app.exec_())        # Window exit condition