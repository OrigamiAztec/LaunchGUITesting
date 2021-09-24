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
#    gc/srt_gc_launchGui/srt_gc_launchDebug.sh
#
#Developers:
#    (C) Doddanavar, Roshan    20181223
#    (L) Doddanavar, Roshan    2019####
#
#Description:
#    Debug script; executes main GUI script within "pdb" (Python Debugger) module. Passes
#    unique pdb commands to execute up until last line, allowing for GUI creation while
#    maintaining python environment (variable workspace).
#    
#    See documentation for "pdb". Good luck 
#
#    CLI execution: "sh ./srt_gc_launchDebug.sh"
#
#Input(s):
#    <None>
#    
#Output(s):
#    <None>

FILE="srt_gc_launchGui.py"
PY=$(which python3)
NLN=$(($(wc -l < $FILE)+1)) # Add one (1) line to count b/c encoding shebang ignored
OPT="-m pdb -c \"until $NLN\""

COM="$PY $OPT $FILE"
eval $COM
