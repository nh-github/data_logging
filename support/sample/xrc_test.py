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

    def update_plot(self, idleevent):

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

    def mousify(self, event):
        if not 'mouse' in self.data['meta']['sensors']: return
        t = time.clock()
        xpos = -1*event.GetPositionTuple()[0]/100.0+2
        ypos = -1*event.GetPositionTuple()[1]/100.0+2
        self.data['mx']['time'].append(t)
        self.data['mx']['val'].append(xpos)
        self.data['my']['time'].append(t)
        self.data['my']['val'].append(ypos)

        if self.data['meta']['saveFlag']:
            fH = self.data['meta']['fileHandle']
            if 0 == fH.tell():
                #file is empty, write header
                header = "datafile with mouse data\n--\nT,X,T,Y\n"
            fH.write("%.3f,%.3f,%.3f,%.3f\n"%(t,xpos,t,ypos))

    #this accelerometer stuff should be elsewhere, probably
    def setup_accelerometer(self):
        #Create an accelerometer object
        try:
            self.accelerometer = Accelerometer()
            self.accelerometer.setOnAttachHandler(self.AccelerometerAttached)
            self.accelerometer.setOnDetachHandler(self.AccelerometerDetached)
            self.accelerometer.setOnErrorhandler(self.AccelerometerError)
            self.accelerometer.setOnAccelerationChangeHandler(self.AccelerometerAccelerationChanged)
            self.accelerometer.openPhidget()
            self.accelerometer.waitForAttach(100)
            self.accelerometer.setAccelChangeTrigger(0, 0.01)
            self.accelerometer.setAccelChangeTrigger(1, 0.01)
            self.accelerometer.setAccelChangeTrigger(2, 0.01)
        except RuntimeError, e:
            print "problem setting up accelerometer"

    def AccelerometerAttached(self, event):
        device = event.device
        print("Accelerometer %i Attached!" % (device.getSerialNum()))

    def AccelerometerDetached(self, event):
        device = event.device
        print("Accelerometer %i Detached!" % (device.getSerialNum()))

    def AccelerometerError(self, e):
        try:
            source = e.device
            print("Accelerometer %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException, e:
            print("Phidget Exception %i: %s" % (e.code, e.details))

    def AccelerometerAccelerationChanged(self, event):
        if not 'accel' in self.data['meta']['sensors']: return
        source = event.device

        accelTime = time.clock()
        accelVal = event.acceleration
        accelIndex = event.index
        accelLabel= "accel%d"%(accelIndex)
        self.data[accelLabel]['time'].append(accelTime)
        self.data[accelLabel]['val'].append(accelVal)

        if self.data['meta']['saveFlag']:
            fH = self.data['meta']['fileHandle']
            if 0 == fH.tell():
                #file is empty, write header
                header = "datafile with raw accelerometer data\n--\n"
                header += "Time,Channel,Value\n"
                fH.write(header)
            fH.write("%.3f,%d,%.3f\n"%(accelTime, accelIndex, accelVal))


class MyApp(wx.App):

    def OnInit(self):
        self.res = xrc.XmlResource('xrc_test.xrc')
        self.InitFrame()

        self.recFlag = False
        self.recFile = None

        return True

    def InitFrame(self):
        self.frame = self.res.LoadFrame(None, 'FRAME1')
        self.statusBar = self.frame.CreateStatusBar()
        self.panel = xrc.XRCCTRL(self.frame, 'panel1')

        #menu(s)
        self.InitMenu()

        #buttons / controls
        self.quitButton = xrc.XRCCTRL(self.panel, 'quitBut')
        self.quitButton.SetForegroundColour("blue")
        self.recButton = xrc.XRCCTRL(self.panel, 'recBut')
        self.dirButton = xrc.XRCCTRL(self.panel, 'dirBut')
        self.frame.Bind(wx.EVT_BUTTON, self.OnQuit, self.quitButton)
        self.frame.Bind(wx.EVT_TOGGLEBUTTON, self.OnRec, self.recButton)
        self.frame.Bind(wx.EVT_BUTTON, self.OnDir, self.dirButton)

        self.dir_path = xrc.XRCCTRL(self.panel, 'dir_path')

        #assemble plot
        self.plot_container = xrc.XRCCTRL(self.frame,"plotspace")
        self.plot_sizer = wx.BoxSizer(wx.VERTICAL)

        # matplotlib panel itself
        self.plotpanel = PlotPanel(self.plot_container)
        self.plotpanel.init_plot_data()

        # wx boilerplate
        self.plot_sizer.Add(self.plotpanel, 1, wx.EXPAND)
        self.plot_container.SetSizer(self.plot_sizer)

        self.statusBar.SetStatusText('attach accel., select directory, record')
        self.frame.Show(1)
        self.SetTopWindow(self.frame)

    def InitMenu(self):
        """
        setup any/all menus from XRC file
        ref: http://wiki.wxpython.org/UsingXmlResources
        """
        self.frame.Bind(wx.EVT_MENU, self.OnQuit, id=xrc.XRCID("quitMenu"))
        self.frame.Bind(wx.EVT_MENU, self.OnRec, id=xrc.XRCID("recMenu"))
        self.frame.Bind(wx.EVT_MENU, self.OnDir, id=xrc.XRCID("dirMenu"))

    def OnQuit(self, event):
        #wx.MessageBox('Quit Button: %s' % (repr(event)))
        self.frame.Close(True)
        sys.exit()

    def OnRec(self, event):
        """
        This is the event handler for the record button/menu entry

        It would be nice to change the color of the button while refording
        for now, set a flag for record or not and calculate a filename
        """
        if self.recFlag:
            self.recFile.close()
            self.plotpanel.data['meta']['dataPath'] = None
            self.plotpanel.data['meta']['fileHandle'] = None
            self.plotpanel.data['meta']['saveFlag'] = False
            self.recFlag = False
            self.statusBar.SetStatusText("idle")
            self.recButton.SetValue(False)
        else:
            dataDir = self.dir_path.GetString(0,-1)
            if not os.path.isdir(dataDir):
                self.statusBar.SetStatusText("directory is not valid")
                return
            timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            dataFile = "capture-%s.txt"%(timestamp)
            dataPath = os.path.join(dataDir,dataFile)
            self.recFile = open(dataPath,'w')
            self.plotpanel.data['meta']['dataPath'] = dataPath
            self.plotpanel.data['meta']['fileHandle'] = self.recFile
            self.plotpanel.data['meta']['saveFlag'] = True
            self.recFlag = True
            self.statusBar.SetStatusText("recording")
            self.recButton.SetValue(True)

    def OnDir(self, event):
        dlg = wx.DirDialog(self.frame, "Choose a directory:",
            style=wx.DD_DEFAULT_STYLE
            #| wx.DD_DIR_MUST_EXIST
            #| wx.DD_CHANGE_DIR
            )

        if dlg.ShowModal() == wx.ID_OK:
            self.dir_path.Clear()
            self.dir_path.AppendText(dlg.GetPath()) 
            #self.log.WriteText('You selected: %s\n' % dlg.GetPath())

        #wx.MessageBox('Record Button: %s, %s' % (type(a),repr(a)))
        #b = self.dir_path.GetString(0,-1)
        #wx.MessageBox('Record Button: %s, %s' % (type(b),b))


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()

