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
    gc/srt_gc_launchGui/srt_gc_launchTools.py

Developers:
    (C) Doddanavar, Roshan    20181108
    (L) Doddanavar, Roshan    ########

Description:
    <description>
    
Input(s):
    <none>
    
Output(s):
    <outputs>
'''

# Installed modules --> Utilities
import numpy as np

class Object(object):

    '''
    Empty "Dummy" Container 
    '''
    
    pass

class Tools():

    def resize(self,grid,rowStretch,colStretch):

        '''
        Row & Column Resizing
        '''

        for i in range(len(rowStretch)):
            grid.setRowStretch(i,rowStretch[i])

        for i in range(len(colStretch)):
            grid.setColumnStretch(i,colStretch[i])

    def extrap(self,t,x,tq,dt):

        '''
        Data Extrapolation
        '''

        # No. past values to use in linear fit
        n = int(round(tq/dt))

        if (n < len(t)):

            # Use all past packets
            dxdt = (x[-1] - x[-n])/(t[-1] - t[-n])

        else:

            # Only use past n packets
            dxdt = (x[-1] - x[0])/(t[-1] - t[0])

        xq = x[-1] + tq*dxdt

        return xq

    def vapPress(self,T0):

        '''
        Determine N2O Vapor Pressure
        '''

        f2r    = 459.67
        r2k    = 0.55556
        pa2psi = 0.0001450377
        G      = [96.512,-4045,-12.277,0.0000289,2]

        T0     = (T0 + f2r)*r2k                                                      
        pSat0  = np.exp(G[0] + G[1]/T0 + G[2]*np.log(T0) + G[3]*pow(T0,G[4])) # Initial vapor pressure of N2O [Pa]
        pSat0  = pSat0*pa2psi

        return pSat0