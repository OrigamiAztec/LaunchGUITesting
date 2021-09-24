# -*- codingutf-8 -*-
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
    gc/srt_gc_launchGui/srt_gc_launchStyle.py

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

# Installed modules --> PyQt related
from PyQt5 import QtCore
import pyqtgraph as pg

# Program modules
from srt_gc_launchTools import Object

class Color():

    '''
    UI Color Definition 
    '''

    # Control button colors via CSS
    comm = "gray"
    sys  = "gray"
    abt  = "magenta"
    daq  = "goldenrod"
    n2o  = "darkCyan"
    qd   = "chocolate"
    o2   = "green"
    ign  = "red"
    bvas = "#3776ab"
    mdot = "#3776ab"
    av   = "gray"

class Style():

    # Font sizes - no space between value & unit
    fontLarge  = "20px"
    fontMedium = "18px"
    fontSmall  = "14px"

    # Text formatting via CSS style sheets
    css     = Object() # Container for CSS style sheet strings(s)
    cssSpec = Object() # " " CSS style sheet fields 

    cssSpec.window    = [("background-color", "rgb(44, 44, 44)")]
    cssSpec.group     = [("font-weight", "normal"), ("font-size", fontSmall)]
    cssSpec.groupComm = [("font-weight",   "bold"), ("font-size", fontSmall)]
    cssSpec.title     = [("font-weight",   "bold"), ("font-size", fontLarge)]
    cssSpec.subtitle  = [("font-weight",   "bold"), ("font-size", fontSmall)]
    cssSpec.button    = [("font-weight", "normal"), ("font-size", fontSmall)]
    cssSpec.axes      = [("font-weight",   "bold"), ("font-size", fontSmall)]
    cssSpec.label     = [("font-weight", "normal"), ("font-size", fontSmall)]
    cssSpec.sensor    = [("font-weight", "normal"), ("font-size", fontSmall), ("background-color", "white")]
    cssSpec.statusBar = [("font-weight", "normal"), ("font-size", fontSmall)]
    cssSpec.error     = [("font-weight",   "bold"), ("font-size", fontSmall), ("color","red")]

    # Plot line formatting
    pen      = Object()
    penWidth = 3

    pen.press       = pg.mkPen('r',width=penWidth)
    pen.pressExtrap = pg.mkPen('r',width=penWidth,style=QtCore.Qt.DotLine)
    pen.temp        = pg.mkPen('r',width=penWidth)
    pen.tempExtrap  = pg.mkPen('r',width=penWidth,style=QtCore.Qt.DotLine)

    def __init__(self):

        '''
        Constructor
         - Converts css spec into style sheet syntax
        '''

        name  = list(self.cssSpec.__dict__)
        style = [None]*len(name)
   
        for i in range(len(name)):
            
            spec    = getattr(self.cssSpec,name[i])
            specStr = "" 

            for j in range(len(spec)):
                specStr += spec[j][0] + ": " + spec[j][1] + "; "

            style[i] = specStr

        for i in range(len(name)):   
            setattr(self.css,name[i],style[i]) # Assign CSS style sheet strings

    def setButton(self,color):

        '''
        Button Style Generator
        '''

        style = self.css.button + "background-color: " + color + "; "

        return style