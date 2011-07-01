#! /usr/bin/env pythonw

import collections
import os
import numpy
import sys
import time
import wx


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
        self.datastore = collections.deque()

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
        print "button: %s, at T==%f, val==%f"%(btnLabel, t, value)
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


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Simple wxPython App")
        self.SetTopWindow(frame)

        print "Print statements go to this stdout window by default."

        frame.Show(True)
        return True
        
app = MyApp(redirect=True)
app.MainLoop()
