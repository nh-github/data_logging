#!/usr/bin/env python
"""
Copyright (C) 2003-2005 Jeremy O'Donoghue and others

License: This work is licensed under the PSF. A copy should be included
with this source code, and is also available at
http://www.python.org/psf/license.html

from:
  /opt/local/share/py25-matplotlib/examples/animation/dynamic_image_wxagg2.py

"""
import sys, time, os, gc

import matplotlib
matplotlib.use('WXAgg')

from matplotlib import rcParams
import numpy as npy

import matplotlib.cm as cm

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure
#from wx import *

import pylab
import wx


TIMER_ID = wx.NewId()

class PlotFigure(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Test embedded wxFigure")

        self.fig = Figure((5,4), 75)    #matplotlib.figure
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig) #also matplotlib
        self.toolbar = NavigationToolbar2Wx(self.canvas) #again matplotlib
        self.toolbar.Realize()

        # On Windows, default frame size behaviour is incorrect
        # you don't need this under Linux
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))

        # Create a figure manager to manage things

        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        # Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()
        wx.EVT_TIMER(self, TIMER_ID, self.onTimer)

    def init_plot_data(self):
        # jdh you can add a subplot directly from the fig rather than
        # the fig manager
        self.ax = self.fig.add_axes([0.075,0.1,0.75,0.85])
        cax = self.fig.add_axes([0.85,0.1,0.075,0.85])
        #self.x = npy.empty((120,120))
        #self.x.flat = npy.arange(120.0)*2*npy.pi/120.0
        #self.y = npy.empty((120,120))
        #self.y.flat = npy.arange(120.0)*2*npy.pi/100.0
        #self.y = npy.transpose(self.y)
        #z = npy.sin(self.x) + npy.cos(self.y)
        #self.im = a.imshow( z, cmap=cm.jet)#, interpolation='nearest')
        #self.x = npy.arange(100)
        self.x = npy.arange(0,1,0.01)

        self.y = npy.cos(2*npy.pi*self.x)
        #self.im = self.a.plot(self.x,self.y)
        self.dataplot , = pylab.plot(self.x, npy.sin(self.x), animated=True, lw=2)
        #self.fig.colorbar(self.im,cax=cax,orientation='vertical')

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    def onTimer(self, evt):
        return
        #self.x += npy.pi/15
        #self.y += npy.pi/20
        #z = npy.sin(self.x) + npy.cos(self.y)
        #self.im.set_array(z)
        self.x += 10
        self.y = npy.cos(2*npy.pi*self.x)
        self.dataplot  
        self.canvas.draw()
        #self.canvas.gui_repaint()  # jdh wxagg_draw calls this already

    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = PlotFigure()
    frame.init_plot_data()

    # Initialise the timer - wxPython requires this to be connected to
    # the receiving event handler
    t = wx.Timer(frame, TIMER_ID)
    t.Start(100)

    frame.Show()
    app.MainLoop()

