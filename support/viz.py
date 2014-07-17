#! /usr/bin/env python
"""
plot data acquired by an arduino (serial connection)
ref:
    https://gist.github.com/electronut/d5e5f68c610821e311b0/raw/ldr.py
    https://stackoverflow.com/questions/5160558/how-to-update-a-plot-\
            with-python-and-matplotlib
"""
import glob
import platform
import serial

import wx
import matplotlib as mpl
mpl.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas


class Plot(wx.Panel):
    def __init__(self, parent, id=-1, dpi=None, **kwargs):
        wx.Panel.__init__(self, parent, id=id, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2, 2))
        self.canvas = Canvas(self, -1, self.figure)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)


class JBC(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(600, 600))
        self.SetBackgroundColour(wx.Colour(236, 233, 216))

        self.nbG = wx.Notebook(self, -1, style=0, size=(400, 400),
                               pos=(0, 0))
        self.gSheet1 = self.add("Test").gca()

        calcButton = wx.Button(self, wx.NewId(), "Update",
                               pos=(0, self.nbG.Position.y + 400))

        #self.gSheet1.hold(False)
        #self.gSheet1.set_xlim(0,20)
        #self.gSheet1.set_ylim(0,20)
        #for i in range (2):
        #    self.gSheet1.plot([0,10],[1*i,1+i])

        #axes2 = plotter.add('figure 2').gca()
        #axes2.plot([1,2,3,4,5],[2,1,4,2,3])

        self.Bind(wx.EVT_BUTTON, self.OnCalculate, calcButton)
        # self.Show(True)

    def OnCalculate(self, event):
        self.gSheet1.set_xlim(0, 20)
        self.gSheet1.set_ylim(0, 20)
        self.gSheet1.plot([1, 2, 3, 4, 5], [2, 1, 4, 2, 3])
        self.Update()

    def add(self, name="plot"):
        page = Plot(self.nbG)
        self.nbG.AddPage(page, name)
        return page.figure

    def Update(self):
        self.gSheet1.clear()
        plt.draw()
        print "Tried to redraw"


class data_aquisition_tool():
    def port_scan(self):
        ser = serial.Serial()
        for port in self.port_list():
            #print port
            ser.port = port
            ser.baudrate = 115200
            ser.timeout = 1  # timeout block read
            try:
                ser.open()
            except Exception, e:
                pass
                e = e
                #print "error open serial port: " + str(e)

            if ser.isOpen():
                ser.flushInput()
                n = 25
                while n > 0:
                    n -= 1
                    response = ser.readline()
                    if "#MFE" in response:
                        #bad form, but better than alternatives
                        return ser

    def read_data_frame(self, serial_port):
        # flags for loop
        start = False
        done = False
        data_frame_lines = [""]
        while not done:
            line = serial_port.readline()
            if "#MFB" in line:
                start = True
            if "#MFE" in line:
                done = True
            if start:
                data_frame_lines.append(line)
        return data_frame_lines

    def port_list(self):
        if platform.system() == "Windows":
            # Scan for available ports.
            available = []
            for i in range(256):
                try:
                    s = serial.Serial(i)
                    available.append(i)
                    s.close()
                except serial.SerialException:
                    pass
            return available
        elif platform.system() == "Darwin":
            return glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
        else:
            # Assume Linux or something else
            return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')


def main():
    print "data plotting"
    daq = data_aquisition_tool()
    daq_port = daq.port_scan()
    print("DEBUG: reading from serial port %s..." % daq_port.port)

    df = daq.read_data_frame(daq_port)
    print df
    plt == plt

if "__main__" == __name__:
    #main()
    app = wx.App()
    frame = JBC(None, -1, "Test Title")
    frame.Show()
    app.MainLoop()
