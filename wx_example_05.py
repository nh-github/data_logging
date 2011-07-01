# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import numpy as np
import wx
import wx.aui
import matplotlib as mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar

class Plot(wx.Panel):
    def __init__(self, parent, id = -1, dpi = None, **kwargs):
        wx.Panel.__init__(self, parent, id=id, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2,2))
        self.canvas = Canvas(self, -1, self.figure)
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,1,wx.EXPAND)
        sizer.Add(self.toolbar, 0 , wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)

class PlotNotebook(wx.Panel):
    def __init__(self, parent, id = -1):
        wx.Panel.__init__(self, parent, id=id)
        self.nb = wx.aui.AuiNotebook(self)
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def add(self,name="plot"):
       page = Plot(self.nb)
       self.nb.AddPage(page,name)
       return page.figure


def update_plot(idleevent):
    return

def demo():
    app = wx.PySimpleApp()
    frame = wx.Frame(None,-1,'Plotter')
    plotter = PlotNotebook(frame)
    x = np.arange(0,1,0.01)
    y = np.cos(2*np.pi*x)
    axes1 = plotter.add('figure 1').gca()
    axes1.plot(x,y)
    #axes2 = plotter.add('figure 2').gca()
    #axes2.plot([1,2,3,4,5],[2,1,4,2,3])
    #axes1.figure.canvas.draw()
    #axes2.figure.canvas.draw()
    #
    quitButton = wx.Button(frame, -1, "quit")
    recButton = wx.Button(frame, -1, "record")
    buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
    buttonSizer.Add(quitButton,0)
    buttonSizer.Add(recButton,0)
    #
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(buttonSizer,0,wx.EXPAND)
    sizer.Add(plotter,1,wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Show()

    wx.EVT_IDLE(wx.GetApp(), update_plot)

    app.MainLoop()

if __name__ == "__main__": demo()

