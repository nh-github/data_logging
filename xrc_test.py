#! /usr/bin/env python

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.cm as cm
import matplotlib.cbook as cbook
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
from matplotlib.figure import Figure
import numpy as npy

import os
import sys
import time
import wx
from wx import xrc
from wx.lib import  filebrowsebutton 


ERR_TOL = 1e-5 # floating point slop for peak-detection


# Define File Drop Target class
class FileDropTarget(wx.FileDropTarget):
    """ This object implements Drop Target functionality for Files """
    def __init__(self, obj):
        """ Initialize the Drop Target, passing in the Object Reference to
            indicate what should receive the dropped files """
        # Initialize the wxFileDropTarget Object
        wx.FileDropTarget.__init__(self)
        # Store the Object Reference for dropped files
        self.obj = obj

    def OnDropFiles(self, x, y, filenames):
        """ Implement File Drop """
        # For Demo purposes, this function appends a list of the files dropped at the end of the widget's text
        # Move Insertion Point to the end of the widget's text
        self.obj.SetInsertionPointEnd()
        # append a list of the file names dropped
        self.obj.WriteText("%d file(s) dropped at %d, %d:\n" % (len(filenames), x, y))
        for file in filenames:
            self.obj.WriteText(file + '\n')
        self.obj.WriteText('\n')
        print 'drop'


class PlotPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.fig = Figure((5,4), 75)
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        #self.toolbar = Toolbar(self.canvas) #matplotlib toolbar
        #self.toolbar.Realize()
        #self.toolbar.set_active([0,1])

        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        #sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        sizer.Add(self.canvas, 1, wx.ALL|wx.GROW)
        # Best to allow the toolbar to resize!
        #sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()

    def init_plot_data(self):
        a = self.fig.add_subplot(111)

        x = npy.arange(120.0)*2*npy.pi/60.0
        y = npy.arange(100.0)*2*npy.pi/50.0
        self.x, self.y = npy.meshgrid(x, y)
        z = npy.sin(self.x) + npy.cos(self.y)
        self.im = a.imshow( z, cmap=cm.jet)#, interpolation='nearest')

        zmax = npy.amax(z) - ERR_TOL
        ymax_i, xmax_i = npy.nonzero(z >= zmax)
        if self.im.origin == 'upper':
            ymax_i = z.shape[0]-ymax_i
        self.lines = a.plot(xmax_i,ymax_i,'ko')

        #self.toolbar.update() # Not sure why this is needed - ADS

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass


class MyApp(wx.App):

    def OnInit(self):
        self.res = xrc.XmlResource('xrc_test.xrc')
        self.init_frame()
        return True

    def init_frame(self):
        self.frame = self.res.LoadFrame(None, 'FRAME1')
        self.panel = xrc.XRCCTRL(self.frame, 'panel1')
        #self.text1 = xrc.XRCCTRL(self.panel, 'text1')
        #self.text2 = xrc.XRCCTRL(self.panel, 'text2')
        #self.frame.Bind(wx.EVT_BUTTON, self.OnSubmit, id=xrc.XRCID('button'))
        self.quitButton = xrc.XRCCTRL(self.panel, 'quitBut')
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

        self.frame.Show(1)
        self.SetTopWindow(self.frame)

    def OnQuit(self, event):
        #wx.MessageBox('Quit Button: %s' % (repr(event)))
        self.frame.Close(True)

    def OnRec(self, event):
        a = event.IsChecked()
        #wx.MessageBox('Record Button: %s, %s' % (type(a),repr(a)))
        b = self.dir_path.GetString(0,-1)
        wx.MessageBox('Record Button: %s, %s' % (type(b),b))

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

