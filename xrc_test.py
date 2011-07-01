#! /usr/bin/env python

import wx
from wx import xrc

class MyApp(wx.App):

    def OnInit(self):
        self.res = xrc.XmlResource('test_01.xrc')
        self.init_frame()
        return True

    def init_frame(self):
        self.frame = self.res.LoadFrame(None, 'mainFrame')
        self.panel = xrc.XRCCTRL(self.frame, 'panel')
        self.text1 = xrc.XRCCTRL(self.panel, 'text1')
        self.text2 = xrc.XRCCTRL(self.panel, 'text2')
        #self.frame.Bind(wx.EVT_BUTTON, self.OnSubmit, id=xrc.XRCID('button'))
        self.button = xrc.XRCCTRL(self.panel, 'button')
        self.frame.Bind(wx.EVT_BUTTON, self.OnSubmit, self.button)
        self.frame.Show(1)
        self.SetTopWindow(self.frame)


    def OnSubmit(self, evt):
        wx.MessageBox('Your name is %s %s!' %
        (self.text1.GetValue(), self.text2.GetValue()), 'Feedback')

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()

