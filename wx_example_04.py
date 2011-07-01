#!/usr/bin/env python
"""
An example of how to use wx or wxagg in an application with a custom
toolbar
"""

# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')


import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg

from matplotlib.backends.backend_wx import _load_bitmap
from matplotlib.figure import Figure

import numpy as np
from numpy import arange, sin, pi
from numpy.random import rand

import time
import wx

class MyNavigationToolbar(NavigationToolbar2WxAgg):
    """
    Extend the default wx toolbar with your own event handlers
    """
    ON_CUSTOM = wx.NewId()
    def __init__(self, canvas, cankill):
        NavigationToolbar2WxAgg.__init__(self, canvas)

        # for simplicity I'm going to reuse a bitmap from wx, you'll
        # probably want to add your own.
        self.AddSimpleTool(self.ON_CUSTOM, _load_bitmap('stock_left.xpm'),
                           'Click me', 'Activate custom contol')
        wx.EVT_TOOL(self, self.ON_CUSTOM, self._on_custom)

    def _on_custom(self, evt):
        # add some text to the axes in a random location in axes (0,1)
        # coords) with a random color

        # get the axes
        ax = self.canvas.figure.axes[0]

        # generate a random location can color
        x,y = tuple(rand(2))
        rgb = tuple(rand(3))

        # add the text and draw
        ax.text(x, y, 'You clicked me',
                transform=ax.transAxes,
                color=rgb)
        self.canvas.draw()
        evt.Skip()


class CanvasFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self,None,-1,
                         'CanvasFrame',size=(550,350))

        timeStart=time.clock()
        self.SetBackgroundColour(wx.NamedColor("WHITE"))

        self.figure = Figure(figsize=(5,4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        #self.x = np.arange(0.0,5.0,0.01)
        #self.y = np.sin(2*np.pi*self.x)

        #self.mouseX = np.arange(0.0,0.1,0.1)
        #self.mouseY = np.arange(0.0,0.1,0.1)
        self.mouseT = [0,time.clock()]
        self.mouseX = [0,0]
        self.mouseY = [0,0]

        self.axes.autoscale(enable=False)
        #self.axes.plot(self.x,self.y)
        #self.axes.set_xlim((self.x.min(), self.x.max()))
        self.axes.plot(self.mouseT,self.mouseX)
        self.axes.plot(self.mouseT,self.mouseY)
        self.axes.set_xlim((self.mouseT[0], self.mouseT[-1]))
        self.axes.set_ylim((-2, 2))

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)
        # Capture the paint message
        wx.EVT_PAINT(self, self.OnPaint)

        id = wx.NewId()
        actor = self.canvas
        self.timer = wx.Timer(actor, id=id)
        self.timer.Start(25)
        wx.EVT_TIMER(actor, id, self.update_plot)

        id = wx.NewId()
        actor = self.canvas
        self.timer2 = wx.Timer(actor, id=id)
        self.timer2.Start(1000)
        wx.EVT_TIMER(actor, id, self.print_update_rate)

        wx.EVT_CLOSE(self.canvas, self.on_close)

        #wx.EVT_IDLE(self, self.update_plot)

        wx.EVT_MOTION(self.canvas, self.mousify)
        #self.Bind(wx.EVT_MOTION, self.mousify)
        #self.canvas.Bind(wx.EVT_MOTION, self.mousify)

        self.toolbar = MyNavigationToolbar(self.canvas, True)
        self.toolbar.Realize()
        if wx.Platform == '__WXMAC__':
            # Mac platform (OSX 10.3, MacPython) does not seem to cope with
            # having a toolbar in a sizer. This work-around gets the buttons
            # back, but at the expense of having the toolbar at the top
            self.SetToolBar(self.toolbar)
        else:
            # On Windows platform, default window size is incorrect, so set
            # toolbar width to figure width.
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            # By adding toolbar in sizer, we are able to put it at the bottom
            # of the frame - so appearance is closer to GTK version.
            # As noted above, doesn't work for Mac.
            self.toolbar.SetSize(wx.Size(fw, th))
            self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)

        # update the axes menu on the toolbar
        self.toolbar.update()
        self.SetSizer(self.sizer)
        self.Fit()

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
        #print 'plot update'
        #self.x += 0.2
        #self.y = np.sin(2*np.pi*self.x)

        self.mouseT.append(time.clock())
        self.mouseX.append(self.mouseX[-1])
        self.mouseY.append(self.mouseY[-1])

        self.axes.clear()
        #self.axes.plot(self.x,self.y)
        self.axes.plot(self.mouseT,self.mouseX)
        self.axes.plot(self.mouseT,self.mouseY)
        #self.axes.set_xlim((self.mouseT[0], self.mouseT[-1]))
        self.axes.set_xlim((time.clock()-5,time.clock()))
        self.axes.set_ylim((-2, 2))
        self.canvas.draw()

        #print self.mouseT

    def print_update_rate(self, event):
        traceTime = self.mouseT[-1] - self.mouseT[0]
        traceLength = len(self.mouseT)
        longSampleRate = traceLength / traceTime
        sampleRate = 1.0/(self.mouseT[-1]-self.mouseT[-2])
        sampleRate2 = 5.0/(self.mouseT[-1]-self.mouseT[-6])
        print "T: %.3f, #pts: %d, avg S/s: %.3f, S/s: %.3f"%(
            traceTime, traceLength, longSampleRate, sampleRate2)

class App(wx.App):

    def OnInit(self):
        'Create the main window and insert the custom frame'
        self.frame = CanvasFrame()
        self.frame.Show(True)

        return True



app = App(0)
app.MainLoop()
