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


print "xrc autogen test"

import wash_data_xrc

class PlotPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        #self.fig = Figure((5,4), 75)
        self.fig = Figure(figsize=(3.75,2.75), dpi=100)

        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        #self.toolbar = Toolbar(self.canvas) #matplotlib toolbar
        #self.toolbar.Realize()
        #self.toolbar.set_active([0,1])

        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # This way of adding to sizer allows resizing
        #sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        sizer.Add(self.canvas, 1, wx.ALL|wx.GROW|wx.ALIGN_CENTER_VERTICAL|
                wx.ALIGN_CENTER_HORIZONTAL)
        # Best to allow the toolbar to resize!
        #sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()

    def init_plot_data(self):
        self.axes = self.fig.add_subplot(111)

        timeStart=time.clock()

        return

        self.data = {}#use a dictionary of paired lists
        # data := (trace|metadata) *
        # trace := time [], val []
        # time := (timeN)*
        # val := (valN)*
        # timeN := float
        # valN := float
        self.data['meta'] = {'saveFlag':False,
            'dataPath':None,
            'fileHandle':None,
            'sensors':[]}
        #if 'Accelerometer' in globals():
        try:
            self.setup_accelerometer()
            self.data['meta']['sensors'].append('accel')
        except:
            print 'accelerometer not setup'
            self.data['meta']['sensors'].append('mouse')
        #else:
            #print 'no accelerometer, using mouse position'

        print self.data['meta']['sensors']

        if 'accel' in self.data['meta']['sensors']: 
            print 'set initial accel data'
            self.data['accel0'] = {'time':[0,time.clock()],'val':[0,0.0]}
            self.data['accel1'] = {'time':[0,time.clock()],'val':[0,0.0]}
            self.data['accel2'] = {'time':[0,time.clock()],'val':[0,0.0]}
        if 'mouse' in self.data['meta']['sensors']: 
            print 'set initial mouse data'
            self.data['mx'] = {'time':[0,time.clock()],'val':[0,0.0]}
            self.data['my'] = {'time':[0,time.clock()],'val':[0,0.0]}

        #self.axes.autoscale(enable=False)
        #maxTime = 0
        #for key in self.data.keys():
        #    if 'meta' == key: continue
        #    x = self.data[key]['time']
        #    y = self.data[key]['val']
        #    self.axes.plot(x,y)
        #    if x[-1] > maxTime:
        #        maxTime = x[-1]
        #self.axes.set_xlim((maxTime-5, maxTime))
        #self.axes.set_ylim((-2, 2))

        wx.EVT_PAINT(self, self.OnPaint)

        id = wx.NewId()
        actor = self.canvas
        self.timer = wx.Timer(actor, id=id)
        self.timer.Start(25)
        wx.EVT_TIMER(actor, id, self.update_plot)

        wx.EVT_MOTION(self.canvas, self.mousify)

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass

    def OnPaint(self, event):
        self.canvas.draw()
        event.Skip()

    def on_close(self, event):
        self.timer.Stop()
        #self.frame.Destroy()
        event.Skip()

    def update_plot(self, event):

        #extend traces
        for key in self.data.keys():
            if 'meta' == key: continue
            self.data[key]['time'].append(time.clock())
            self.data[key]['val'].append( self.data[key]['val'][-1])

        #plot extended traces
        self.axes.clear()
        maxTime = 0
        for key in self.data.keys():
            if 'meta' == key: continue
            x = self.data[key]['time']
            y = self.data[key]['val']
            try:
                assert(len(x)==len(y))
                self.axes.plot(x,y)
            except Exception, e:
                print "big trouble in little plot!"
                print 'key:',key,'lenX',len(x),'lenY',len(y),len(x)==len(y)
                print type(x),type(y)
                raise e
            if x[-1] > maxTime:
                maxTime = x[-1]
        self.axes.set_xlim((maxTime-5, maxTime))
        self.axes.set_ylim((-2, 2))

        self.canvas.draw()

    def plot_data(self, data):
        self.axes.clear()
        minTimes = []
        maxTimes = []
        for key in data['traces'].keys():
            x = data['traces'][key]['time']
            y = data['traces'][key]['val']
            try:
                assert(len(x)==len(y))
                self.axes.plot(x,y)
            except Exception, e:
                print "big trouble in little plot!"
                print 'key:',key,'lenX',len(x),'lenY',len(y),len(x)==len(y)
                print type(x),type(y)
                raise e
            maxTimes.append(x[-1])
            minTimes.append(x[0])
        self.axes.set_xlim((min(minTimes), max(maxTimes)))
        self.axes.set_ylim((-2, 2))

        self.canvas.draw()


class autoFrame(wash_data_xrc.xrcFRAME1):
    def __init__(self):
        """Constructor"""
        wash_data_xrc.xrcFRAME1.__init__(self, parent=None)

        self.Bind(wx.EVT_BUTTON, self.OnQuit, self.quitBut)
        self.Bind(wx.EVT_BUTTON, self.OnFile, self.fileBut)
        self.Bind(wx.EVT_BUTTON, self.OnRec, self.writeBut)

        self.InitMenu()

        #setup the plotting area
        #assemble plot
        self.plot_container = xrc.XRCCTRL(self,"plotspace")
        self.plot_sizer = wx.BoxSizer(wx.VERTICAL)

        # matplotlib panel itself
        self.plotpanel = PlotPanel(self.plot_container)
        self.plotpanel.init_plot_data()

        # wx boilerplate
        self.plot_sizer.Add(self.plotpanel, 1, wx.EXPAND)
        self.plot_container.SetSizer(self.plot_sizer)

        #statusbar
        self.statusBar = self.CreateStatusBar()

        self.Show()

    def InitMenu(self):
        """
        setup any/all menus from XRC file
        ref: http://wiki.wxpython.org/UsingXmlResources
        """
        self.Bind(wx.EVT_MENU, self.OnQuit, id=xrc.XRCID("quitMenu"))
        self.Bind(wx.EVT_MENU, self.OnRec, id=xrc.XRCID("recMenu"))
        self.Bind(wx.EVT_MENU, self.OnFile, id=xrc.XRCID("openMenu"))
        
    def OnQuit(self, event):
        #wx.MessageBox('Quit Button: %s' % (repr(event)))
        self.Close(True)
        sys.exit()

    def OnDir(self, event):
        dlg = wx.DirDialog(self.frame, "Choose a directory:",
            style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR
            )

        if dlg.ShowModal() == wx.ID_OK:
            self.dir_path.Clear()
            self.dir_path.AppendText(dlg.GetPath()) 

    def OnFile(self, event):
        wildcard =  "text (*.txt)|*.txt|"   \
                    "csv (*.csv)|*.csv|"   \
                    "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, "Choose a file:",
            wildcard=wildcard,
            style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR
            )

        if dlg.ShowModal() == wx.ID_OK:
            self.file_path.Clear()
            self.file_path.AppendText(dlg.GetPath()) 
            self.statusBar.SetStatusText('file selected')
        self.fileData = self.loadFile(self.file_path.GetString(0,-1))
        self.plotpanel.plot_data(self.fileData)

    def OnRec(self, event):
        """
        Call this to write the reformatted/retimed files

        It would be nice to change the color of the button while refording
        for now, set a flag for record or not and calculate a filename
        """
        #load and plot data in OnFile()
        self.nameFile(self.fileData)
        self.saveFile(self.fileData)
        #save
        #interpolate
        #save

    def loadFile(self, path):
        try:
            infile = open(path)
            self.statusBar.SetStatusText('file opened')
        except:
            self.statusBar.SetStatusText('problem with file')

        data = {'meta':{},'traces':{}}
        data['meta']['filePath'] = path
        lineCount = 0
        errorCount = 0
        for line in csv.reader(infile):
            lineCount += 1
            try:
                pointTime = float(line[0])
                pointChan = line[1]
                pointVal = float(line[2])
            except:
                errorCount += 1
                continue
            if not pointChan in data['traces']:
                dataPoint = {'time':[pointTime],'val':[pointVal]}
                data['traces'][pointChan] = dataPoint
            else:
                data['traces'][pointChan]['time'].append(pointTime)
                data['traces'][pointChan]['val'].append(pointVal)
        self.statusBar.SetStatusText('file read: %d errors in %d lines'%(errorCount,lineCount))
        return data

    def nameFile(self, data):
        #print data['meta']
        inName = data['meta']['filePath']

        name0,name1 = os.path.splitext(inName)
        outName0 = name0+'-sorted'+name1
        outName1 = name0+'-retimed'+name1
        #print "writing traces from:\n  %s\nto:\n  %s"%(inName, outName0)
        #print "writing traces from:\n  %s\nto:\n  %s"%(inName, outName1)
        data['meta']['filePathSorted'] = outName0
        data['meta']['filePathTimed'] = outName1

    def saveFile(self, data):
        #traceNames = data['traces'].keys()
        #traceNames.sort()
        self.procAdjTime(data)
        self.procExtendTraces(data)
        self.genOutArray(data)
        self.saveFileSorted(data)
        self.interpolateTraces(data)
        self.saveFileTimed(data)

        data['meta']['filePathTimed']

    def procAdjTime(self, data):
        traceNames = data['traces'].keys()
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
        data['meta']['timing'] = {'maxLen':maxLen,'arrWidth':arrWidth,
                'Times':[startTime,endTime]}

    def procExtendTraces(self, data):
        traceNames = data['traces'].keys()
        maxLen = data['meta']['timing']['maxLen']

        for TI in traceNames:
            traceTime = data['traces'][TI]['time']
            traceVal = data['traces'][TI]['val']
            traceLen = min(len(traceTime), len(traceVal))
            for i in range(maxLen):
                if i<traceLen:
                    pointTime = traceTime[i]
                    pointVal = traceVal[i]
                else:
                    pointTime = 0
                    pointVal = 0

    def genOutArray(self, data):
        traceNames = data['traces'].keys()
        traceNames.sort()
        maxLen = data['meta']['timing']['maxLen']
        arrWidth = data['meta']['timing']['arrWidth']
        startTime, endTime = data['meta']['timing']['Times']
        outputArray = np.zeros([maxLen, arrWidth])
        outputArray = np.zeros([arrWidth, maxLen])
        traceIndex = -2 #I want to increment this at the start of the loop
        for traceName in traceNames:
            traceIndex += 2
            traceTime = data['traces'][traceName]['time']
            traceVal = data['traces'][traceName]['val']
            traceLen = min(len(traceTime), len(traceVal))
            a = np.array(traceTime)
            b = np.array(traceVal)
            c = np.array([a,b])
            outputArray[traceIndex,0:traceLen] = np.array(traceTime)-startTime
            outputArray[traceIndex+1,0:traceLen] = np.array(traceVal)
        data['npTraceBlocks'] = {'sorted':outputArray.T}

    def saveFileSorted(self, data):
        traceKeys = data['traces'].keys()
        traceKeys.sort()
        traceNames = []
        for name in traceKeys:
            traceNames.append('time')
            traceNames.append(name)
        outFile = open(data['meta']['filePathSorted'],'w')
        csvOut = csv.writer( outFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        outFile.write('sorted raw trace data\n--\n')
        csvOut.writerow(traceNames)
        csvOut.writerows(data['npTraceBlocks']['sorted'])
        outFile.close()
        self.statusBar.SetStatusText('file written: %s'%(data['meta']['filePathSorted']))

    def interpolateTraces(self, data):
        traceNames = data['traces'].keys()
        traceNames.sort()
        maxLen = data['meta']['timing']['maxLen']
        arrWidth = data['meta']['timing']['arrWidth']
        startTime, endTime = data['meta']['timing']['Times']
        traceIndex = -2 #I want to increment this at the start of the loop

        newTimes = np.arange(0,endTime-startTime,0.01)
        newOutArr = np.array(newTimes)
        for traceName in traceNames:
            traceTime = np.array(data['traces'][traceName]['time'])-startTime
            traceVal = np.array(data['traces'][traceName]['val'])
            traceLen = min(len(traceTime), len(traceVal))
            traceInterp = spInterp(traceTime, traceVal)
            newVals = traceInterp(newTimes)
            newOutArr = np.row_stack([newOutArr, newVals])
        data['npTraceBlocks']['timed'] = newOutArr.T

    def saveFileTimed(self, data):
        traceNames= data['traces'].keys()
        traceNames.sort()
        traceNames.insert(0,'time')

        outFile = open(data['meta']['filePathTimed'],'w')
        csvOut = csv.writer( outFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        outFile.write('retimed trace data\n--\n')
        csvOut.writerow(traceNames)
        csvOut.writerows(data['npTraceBlocks']['timed'])
        outFile.close()
        self.statusBar.SetStatusText('file written: %s'%(data['meta']['filePathTimed']))

class MyApp(wx.App):

    def OnInit(self):
        frame = autoFrame()
        self.SetTopWindow(frame)
        frame.Show()
        return True


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()



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

