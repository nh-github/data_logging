#! /usr/bin/env python

#Support for Phidgets libs
#really?
from ctypes import *

import datetime
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.cm as cm
import matplotlib.cbook as cbook
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
from matplotlib.figure import Figure
import numpy as np

import os

#Phidgets libs
try:
    from Phidgets.Phidget import Phidget
    from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
    from Phidgets.Events.Events import AccelerationChangeEventArgs, AttachEventArgs, DetachEventArgs, ErrorEventArgs
    from Phidgets.Devices.Accelerometer import Accelerometer
except:
    print 'problem importing Phidgets libs'

import sys
import time
import wx
from wx import xrc
from wx.lib import  filebrowsebutton 


#new libs
import csv
from scipy.interpolate import interp1d as spInterp



print '\ndata washing\n'

#read a file from argv
try:
    infile = open(sys.argv[1])
    #dataFileLines = open(infile).readlines()[3:]
except:
    print "problem opening data file"
    sys.exit(1)

#sort the data into traces
data = {'meta':{},'traces':{}}
for line in csv.reader(infile):
    #if 3>len(line): continue
    try:
        pointTime = float(line[0])
        pointChan = line[1]
        pointVal = float(line[2])
    except:
        continue
    if not pointChan in data['traces']:
        data['traces'][pointChan] = {'time':[pointTime],'val':[pointVal]}
    else:
        data['traces'][pointChan]['time'].append(pointTime)
        data['traces'][pointChan]['val'].append(pointVal)

#print data['traces']['0']

#write traces to a file
#print 'naming'
inName = sys.argv[1]
name0,name1 = os.path.splitext(inName)
outName = name0+'-sorted'+name1
outName1 = name0+'-retimed'+name1
print "writing traces from:\n  %s\nto:\n  %s"%(inName, outName)
outfile = open(outName,'w')
print "writing traces from:\n  %s\nto:\n  %s"%(inName, outName1)
outFileRetime = open(outName1,'w')

traceNames = data['traces'].keys()
traceNames.sort()
maxLen = 0
arrWidth = 0
startTime = 0
endTime = None
for TI in traceNames:
    traceTime = data['traces'][TI]['time']
    traceVal = data['traces'][TI]['val']
    #print len(traceTime), len(traceVal)
    traceLen = min(len(traceTime), len(traceVal))
    maxLen = max(maxLen, traceLen)
    arrWidth += 2
    startTime = max(startTime,traceTime[0])
    if not endTime:
        endTime = traceTime[-1]
    else:
        endTime = min(endTime,traceTime[-1])

for TI in traceNames:
    traceTime = data['traces'][TI]['time']
    traceVal = data['traces'][TI]['val']
    traceLen = min(len(traceTime), len(traceVal))
    print TI
    for i in range(maxLen):
        if i<traceLen:
            pointTime = traceTime[i]
            pointVal = traceVal[i]
        else:
            pointTime = 0
            pointVal = 0
        #print "t %.3f, v %.3f"%(pointTime,pointVal)

outputArray = np.zeros([maxLen, arrWidth])
outputArray = np.zeros([arrWidth, maxLen])
traceIndex = -2 #I want to increment this at the start of the loop
for traceName in traceNames:
    traceIndex += 2
    traceTime = data['traces'][traceName]['time']
    traceVal = data['traces'][traceName]['val']
    traceLen = min(len(traceTime), len(traceVal))
    #print traceName 
    a = np.array(traceTime)
    b = np.array(traceVal)
    c = np.array([a,b])
    outputArray[traceIndex,0:traceLen] = np.array(traceTime)-startTime
    outputArray[traceIndex+1,0:traceLen] = np.array(traceVal)
    #print outputArray[traceIndex,0:traceLen].size,  np.array(traceTime).size
    #print outputArray 

#print outputArray 
outfile.write("sorted data traces\n--\n")
for i in range(maxLen):
    #print outputArray[:,i]
    for j in range(arrWidth):
        #print outputArray[j,i]
        outfile.write("%.3f,"%outputArray[j,i])
    outfile.write("\n")


#use scipy interpolate?

#newTime = np.linspace(0,1,endTime-startTime)
newTimes = np.arange(0,endTime-startTime,0.01)
#newTimes = np.arange(0,2,0.1)
newOutArr = np.array(newTimes)
for traceName in traceNames:
    traceTime = np.array(data['traces'][traceName]['time'])-startTime
    traceVal = np.array(data['traces'][traceName]['val'])
    traceLen = min(len(traceTime), len(traceVal))
    traceInterp = spInterp(traceTime, traceVal)
    newVals = traceInterp(newTimes)

    #print newOutArr.shape
    newOutArr = np.row_stack([newOutArr, newVals])

traceNames.insert(0,'time')
#print traceNames
#print type(traceNames)
csvOut = csv.writer(outFileRetime, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
csvOut.writerow(traceNames)
csvOut.writerows(newOutArr.T)
#print newOutArr.T
#outFileRetime.write("retimed data traces\n--\n")
    #outFileRetime.write("%.3f,"%outputArray[j,i])

#HDF5 / CDF / netcdf?
#np.array data structure?



if __name__ == '__main__':
    pass

