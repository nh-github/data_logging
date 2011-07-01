#! /usr/bin/env pythonw

import collections
import os
import matplotlib
import numpy
import sys
import time
import wxversion
wxversion.ensureMinimal('2.8')

#some of this is from:
#  /opt/local/share/py25-matplotlib/examples/user_interfaces/embedding_in_wx2.py
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import wx

Q_FOR_DATA = collections.deque()

class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(150, 150), size=(350, 300))

        # Create the menubar
        menuBar = wx.MenuBar()

        # and a menu 
        menu = wx.Menu()

        # add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this simple sample")

        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)

        # and put the menu on the menubar
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.CreateStatusBar()
        

        # Now create the Panel to put the other controls on.
        panel = wx.Panel(self)

        # and a few controls
        text = wx.StaticText(panel, -1, "Event testing")
        text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        text.SetSize(text.GetBestSize())
        btn = wx.Button(panel, -1, "Close")
        self.btn1 = wx.Button(panel, -1, "1")
        self.btn2 = wx.Button(panel, -1, "2")
        self.btn3 = wx.Button(panel, -1, "3")
        #self.btn4 = wx.Button(panel, -1, "4")

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnTimeToClose, btn)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton, self.btn1)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton, self.btn2)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton, self.btn3)
        #self.Bind(wx.EVT_BUTTON, self.OnFunButton, self.btn4)

        # Use a sizer to layout the controls, stacked vertically and with
        # a 10 pixel border around each
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 10)
        sizer.Add(self.btn1, 0, wx.ALL, 10)
        sizer.Add(self.btn2, 0, wx.ALL, 10)
        sizer.Add(self.btn3, 0, wx.ALL, 10)
        sizer.Add(btn, 0, wx.ALL, 10)
        #sizer.Add(self.btn4, 0, wx.ALL, 10)
        panel.SetSizer(sizer)
        panel.Layout()

        #store event data in here for now
        self.datastore = Q_FOR_DATA 

    def OnTimeToClose(self, evt):
        """Event handler for the button click."""
        outfile = open('testfile.csv','w')
        #note: this is horrible, not just bad, it is horribly bad
        axes = {}
        for datum in self.datastore:
            t = datum['time']
            c = datum['channel']
            v = datum['value']
            if c not in axes:
                axes[c] = []
            axes[c].append((c,t,v))
        chans = axes.keys()
        chans.sort()
        chanLengths = []
        for chan in chans:
            chanLengths.append(len(axes[chan]))
        maxChLen = max(chanLengths)
        for chan in chans:
            outfile.write("channel,time,value,")
        outfile.write("\n")
        #for i in range(len(axes.items()[0][1])):
        for i in range(maxChLen):
            for chan in chans:
                try:
                    c = axes[chan][i][0]
                    t = axes[chan][i][1]
                    v = axes[chan][i][2]
                    datum = (c,t,v)
                except:
                    datum = ('None',0,0)
                outfile.write("%s,%.3f,%.3f,"%datum)
            outfile.write("\n")

        self.Close()

    def OnFunButton(self, evt):
        """Event handler for the button click."""
        t=time.clock()
        btnLabel = self.FindWindowById(evt.GetId()).GetLabel()
        value = numpy.sin(numpy.pi*t)
        #print "button: %s, at T==%f, val==%f"%(btnLabel, t, value)
        (t, btnLabel)
        datum = {'time':t, 'channel':btnLabel, 'value':value}
        self.datastore.append(datum)
        #print dir(evt)
        #print dir(self.btn4)
        #print 'handle',self.btn4.GetHandle()
        #print 'id',self.btn4.GetId()
        #print 'label',self.btn4.GetLabel()
        #print 'label text',self.btn4.GetLabelText()
        #print 'name',self.btn4.GetName()
        #print ''
        #print 'evt id',evt.GetId()
        #print '?', self.FindWindowById(evt.GetId())
        #print 'evt timestamp',evt.GetTimestamp()
        #print 'evt data',evt.GetClientData()
        #print 'evt object',evt.GetClientObject()
        #print 'evt object',evt.GetEventObject()
        #print 'evt string',evt.GetString()

class CanvasFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,-1,
                         'CanvasFrame',size=(550,350))

        self.SetBackgroundColour(wx.NamedColor("WHITE"))
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        t = numpy.arange(0.0,3.0,0.01)
        s = numpy.sin(2*numpy.pi*t)
    
        self.axes.plot(t,s)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

        #self.add_toolbar()  # comment this out for no toolbar

    def add_toolbar(self):
        self.toolbar = NavigationToolbar2Wx(self.canvas)
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

    def OnPaint(self, event):
        self.canvas.draw()

TIMER_ID = wx.NewId()

class PlotFigure(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Test embedded wxFigure")

        self.fig = Figure((5,4), 75)
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        # On Windows, default frame size behaviour is incorrect
        # you don't need this under Linux
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(Size(fw, th))

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
        a = self.fig.add_axes([0.075,0.1,0.75,0.85])
        cax = self.fig.add_axes([0.85,0.1,0.075,0.85])
        self.x = numpy.empty((120,120))
        self.x.flat = numpy.arange(120.0)*2*numpy.pi/120.0
        self.y = numpy.empty((120,120))
        self.y.flat = numpy.arange(120.0)*2*numpy.pi/100.0
        self.y = numpy.transpose(self.y)

        self.im = a.imshow( z, cmap=cm.jet)#, interpolation='nearest')
        self.fig.colorbar(self.im,cax=cax,orientation='vertical')

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    def onTimer(self, evt): 
        self.x += numpy.pi/15
        self.y += numpy.pi/20
        z = numpy.sin(self.x) + numpy.cos(self.y)
        self.im.set_array(z)
        self.canvas.draw()
        #self.canvas.gui_repaint()  # jdh wxagg_draw calls this already

    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass


class MyApp(wx.App):
    def OnInit(self):
        #frame1 = MyFrame(None, "Simple wxPython App")
        #self.SetTopWindow(frame1)
        #frame1.Show(True)

        #frame2 = CanvasFrame()
        #frame2.Show(True)

        frame3 = PlotFigure()
        frame3.init_plot_data()

        # Initialise the timer - wxPython requires this to be connected to
        # the receiving event handler
        t = Timer(frame3, TIMER_ID)
        t.Start(200)
        frame3.Show(True)

        
        return True
        
app = MyApp(redirect=True)
app.MainLoop()
