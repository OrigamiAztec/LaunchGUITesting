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
    gc/srt_gc_launchGui/srt_gc_launchState.py

Developers:
    (C) Doddanavar, Roshan    20180928
    (L) Doddanavar, Roshan    ########

Description:
    <description>
    
Input(s):
    <none>
    
Output(s):
    <outputs?
'''

class State():

    # Control button character commands
    # name, command

    # System state
    btnComm = [(        "sysArm", 'p'),
               (     "sysDisarm", 'm'),
               (        "ready1", 'r'),
               (        "ready2", 'f'),  
               (         "abort", 'a'),
               (        "buzzOn", 'b'),  
               (       "buzzOff", 'g'),
    # Data acquisition
               (       "sessNew",  ''),
               (    "sessRename",  ''),
               (     "dataState", 'i'),
               (      "avPwrOff", '*'),
               (     "dataStart", 'c'),
               (      "dataStop", 'e'),
    # Fill control
               (    "supplyOpen", '1'),
               (   "supplyClose", '2'),
               (  "supplyVtOpen", '3'),
               ( "supplyVtClose", '4'),
               (     "runVtOpen", '7'),
               (    "runVtClose", '8'),
               (       "motorOn", '0'),
               (      "motorOff", 'y'),
    # Igniter control
               (       "ignCont", 'k'),
               (        "ignArm", 'n'),
               (     "ignDisarm", 'o'),
               (        "oxOpen", '5'),
               (       "oxClose", '6'),
               (         "ignOn", 'l'),
               (        "ignOff", 'h'),
    # Valve control
               (       "bvPwrOn", '_'),
               (      "bvPwrOff", '/'),
               (        "bvOpen", 's'),
               (       "bvClose", '#'),
               (       "bvState", '~'),
               (          "mdot", '!')]  

    commDict = {} # Initialize button command dictionary

    for i in range(len(btnComm)):

        name = btnComm[i][0]
        comm = btnComm[i][1]

        commDict[name] = comm

    # Internal state specification
    # state, positive code, negative code, LED name 

    # System state
    stateSpec = [(   "sysArm",   "xsys1",    "xsys0",   "sysArm"),
                 (   "ready1", "xLBrl11",  "xLBrl10",   "ready1"),
                 (   "ready2", "xLBrl21",  "xLBrl20",   "ready2"),
                 (     "buzz",   "xbuz1",    "xbuz0",     "buzz"),
    # Data acquitision
                 (    "avPwr",  "xebay1",   "xebay0",    "avPwr"),
                 (     "data",  "xdata1",   "xdata0",     "data"),
    # Fill control
                 (   "supply",   "xn2fo",    "xn2fc",   "supply"),
                 ( "supplyVt",   "xn2vo",    "xn2vc", "supplyVt"),
                 (    "runVt",   "xqdao",    "xqdac",    "runVt"),
                 (    "motor",   "xchA1",    "xchA0",    "motor"),
    # Igniter control
                 (  "ignCont",   "xictP",    "xictF",  "ignCont"),
                 (   "ignArm",   "xign1",    "xign0",   "ignArm"),
                 (       "ox",   "xoxyo",    "xoxyc",       "ox"),
                 (      "ign",  "xLBlau", "xLBnolau",      "ign"),
    # Valve control
                 (    "bvPwr",   "xpow1",    "xpow0",    "bvPwr"),
                 (       "bv",  "xbvas1",   "xbvas0",       "bv")]

    stateDict = {} # Initialize state dictionary

    for i in range(len(stateSpec)):

        state   = stateSpec[i][0]
        posCode = stateSpec[i][1]
        negCode = stateSpec[i][2]
        ledName = stateSpec[i][3]

        stateDict[posCode] = (state,True,ledName,"green")
        stateDict[negCode] = (state,False,ledName,"off")

    def __init__(self,led,ledClr):

        self.led    = led    # Gain access to main GUI LED list
        self.ledClr = ledClr # Gain access to LED color pixmaps

        # Defaults internal state(s) to "False"
        for i in range(len(self.stateSpec)):
            
            state = self.stateSpec[i][0]
            setattr(self,state,False)

    def update(self,text):
        
        output  = self.stateDict[text]

        state   = output[0]
        tf      = output[1]
        ledName = output[2]
        pixmap  = output[3]

        # Set internal state True/False
        setattr(self,state,tf)

        # Set LED color w/ corresponding pixmap
        getattr(self.led,ledName).setPixmap(getattr(self.ledClr,pixmap))

    def btnMap(self,name):
        
        comm = self.commDict[name]

        return comm

