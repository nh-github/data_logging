#! /usr/bin/env python

import datetime
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.cm as cm
import matplotlib.cbook as cbook
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
from matplotlib.figure import Figure
import numpy as np

import os
import sys
import time
import wx
from wx import xrc
from wx.lib import  filebrowsebutton 


ERR_TOL = 1e-5 # floating point slop for peak-detection


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

        #self.mouseT = [0,time.clock()]
        #self.mouseX = [0,0]
        #self.mouseY = [0,0]

        self.data = {}
        self.data['mx'] = {'time':[0,time.clock()],'val':[0,0.0]}
        self.data['my'] = {'time':[0,time.clock()],'val':[0,0.0]}
        self.data['x'] = {'time':[0,time.clock()],'val':[0,0.0]}
        self.data['y'] = {'time':[0,time.clock()],'val':[0,0.0]}
        self.data['z'] = {'time':[0,time.clock()],'val':[0,0.0]}
        #self.T = [0,time.clock()]
        #self.x = [0,0]
        #self.y = [0,0]
        #self.z = [0,0]

        self.axes.autoscale(enable=False)
        #self.axes.plot(self.mouseT,self.mouseX)
        #self.axes.plot(self.mouseT,self.mouseY)
        maxTime = 0
        for key in self.data.keys():
            x = self.data[key]['time']
            y = self.data[key]['val']
            self.axes.plot(x,y)
            if x[-1] > maxTime:
                maxTime = x[-1]
        self.axes.set_xlim((maxTime-5, maxTime))
        self.axes.set_ylim((-2, 2))

        #self.canvas = FigureCanvas(self, -1, self.figure)

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
            self.data[key]['time'].append(time.clock())
            self.data[key]['val'].append( self.data[key]['val'][-1])

        #plot extended traces
        self.axes.clear()
        maxTime = 0
        for key in self.data.keys():
            x = self.data[key]['time']
            y = self.data[key]['val']
            self.axes.plot(x,y)
            if x[-1] > maxTime:
                maxTime = x[-1]
        self.axes.set_xlim((maxTime-5, maxTime))
        self.axes.set_ylim((-2, 2))

        self.canvas.draw()

    def mousify(self, event):
        self.data['mx']['time'].append(time.clock())
        self.data['mx']['val'].append(-1*event.GetPositionTuple()[0]/100.0+2)
        self.data['my']['time'].append(time.clock())
        self.data['my']['val'].append(-1*event.GetPositionTuple()[1]/100.0+2)


class MyApp(wx.App):

    def OnInit(self):
        self.res = xrc.XmlResource('xrc_test.xrc')
        self.InitFrame()

        self.recFlag = False
        self.recFile = None
        self.data = {}#use a dictionary of paired lists
        # data := (trace) *
        # trace := time [], val []
        # time := (timeN)*
        # val := (valN)*
        # timeN := float
        # valN := float

        #wx.PostEvent(self.panel, wx.EVT_SIZE())
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

        #timer for dummy data updates
        id = wx.NewId()
        actor = self
        self.timer = wx.Timer(actor, id=id)
        self.timer.Start(500)
        wx.EVT_TIMER(actor, id, self.OnData)

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

    def InitData(self):
        """
        prep data structure / get initial data values
        """
        self.plotpanel.data = {'test':{'time':[0,time.clock()],'val':[0,0]}}
        # data := (trace) *
        # trace := {time [], val []}
        # time := (timeN)*
        # val := (valN)*
        # timeN := float
        # valN := float

    def OnQuit(self, event):
        #wx.MessageBox('Quit Button: %s' % (repr(event)))
        self.frame.Close(True)

    def OnRec(self, event):
        """
        This is the event handler for the record button/menu entry

        It would be nice to change the color of the button while refording
        for now, set a flag for record or not and calculate a filename
        """
        if self.recFlag:
            self.recFile.close()
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

    def OnData(self, event):
        pass
        #self.plotpanel.data['test']['time'].append(time.clock())
        #self.plotpanel.data['test']['val'].append(time.clock())

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()

