#!/bin/bash
#Texas A&M University Sounding Rocketry Team
#SRT-6 | 2018-2019
#
#--------------------------------------------------------------#
#                            TAMU SRT
#  _____                      __  _____          __           __
# / ___/______  __ _____  ___/ / / ___/__  ___  / /________  / /
#/ (_ / __/ _ \/ // / _ \/ _  / / /__/ _ \/ _ \/ __/ __/ _ \/ / 
#\___/_/  \___/\_,_/_//_/\_,_/  \___/\___/_//_/\__/_/  \___/_/  
#                                                                      
#--------------------------------------------------------------#
#
#Filepath:
#    gc/srt_gc_launchGui/srt_gc_launchRun.sh
#
#Developers:
#    (C) Doddanavar, Roshan    20180628
#    (L) Doddanavar, Roshan    2019####
#
#Description:
#    Executes main GUI script w/ proper version of python & associated options.
#    Allows for command line execution to evolve while maintaining interface w/ end user.
#    
#    (idiot-proof GUI execution)
#
#    CLI execution: "sh ./srt_gc_launchRun.sh" 
#
#Input(s):
#    <None>
#    
#Output(s):
#    <None>

FILE="srt_gc_launchGui.py"
PY=$(which python3)
OPT=" -W ignore "

COM=$PY$OPT$FILE
eval $COM
