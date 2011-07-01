#! /usr/bin/env python

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
        self.fig = Figure((2,2), 125)
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

        self.mouseT = [0,time.clock()]
        self.mouseX = [0,0]
        self.mouseY = [0,0]

        self.x = [0,0]
        self.y = [0,0]

        self.axes.autoscale(enable=False)
        self.axes.plot(self.mouseT,self.mouseX)
        self.axes.plot(self.mouseT,self.mouseY)
        self.axes.set_xlim((self.mouseT[0], self.mouseT[-1]))
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

    def mousify(self, event):
        #print 'mouse'
        #print time.clock(), -1*event.GetPositionTuple()[1]/100.0+2
        #print time.clock(), event.GetPosition()[0]/200.0
        self.mouseT.append(time.clock())
        self.mouseX.append(-1*event.GetPositionTuple()[0]/100.0+2)
        self.mouseY.append(-1*event.GetPositionTuple()[1]/100.0+2)

    def update_plot(self, idleevent):
        self.mouseT.append(time.clock())
        self.mouseX.append(self.mouseX[-1])
        self.mouseY.append(self.mouseY[-1])

        self.axes.clear()
        self.axes.plot(self.mouseT,self.mouseX)
        self.axes.plot(self.mouseT,self.mouseY)
        self.axes.set_xlim((time.clock()-5,time.clock()))
        self.axes.set_ylim((-2, 2))
        self.canvas.draw()


class MyApp(wx.App):

    def OnInit(self):
        self.res = xrc.XmlResource('xrc_test.xrc')
        self.InitFrame()

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

    def OnRec(self, event):
        a = event.IsChecked()
        #wx.MessageBox('Record Button: %s, %s' % (type(a),repr(a)))
        #b = self.dir_path.GetString(0,-1)
        #wx.MessageBox('Record Button: %s, %s' % (type(b),b))
        if a:
            self.statusBar.SetStatusText("recording")
        else:
            self.statusBar.SetStatusText("idle")

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

