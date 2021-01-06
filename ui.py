#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Code to make a GUI to run the RiceBraille project using wxPython.

We based this off sample code by Jan Bodnar's ZetCode wxPython tutorial.
sample code author: Jan Bodnar
website: www.zetcode.com
last modified: April 2018
"""

import wx
from tkinter import filedialog as fd
from VideoTracker import VideoTracker

# inherits from wx.Frame, a standard container widget
class BrailleGUI(wx.Frame):

    def __init__(self, parent, title):
        # initialize window params
        super(BrailleGUI, self).__init__(parent, title=title)
        self.auto_page = 0
        self.show_frames = 0
        self.page_length = 0
        self.page_width = 0

        self.InitUI()
        self.Centre()

    def InitUI(self):
        # panel = window on which controls are placed
        panel = wx.Panel(self)

        # obtain system font
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        # we have one vertical sizer, and then a bunch of horizontal sizers inside that vertical sizer
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Box 1: Page Length
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Page Length (cm):')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=8)
        self.page_length = wx.TextCtrl(panel, value="27.94")
        hbox1.Add(self.page_length, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=8, proportion=1)
        vbox.Add(hbox1)

        # box.Add can insert not only widgets, but also empty space
        vbox.Add((-1, 10))

        # Box 2: Page Width
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Page Width (cm):')
        st2.SetFont(font)
        hbox2.Add(st2, flag=wx.LEFT|wx.RIGHT, border=8)
        self.page_width = wx.TextCtrl(panel, value="29.21")
        hbox2.Add(self.page_width, flag=wx.LEFT|wx.RIGHT, border=8, proportion=1)
        vbox.Add(hbox2)

        vbox.Add((-1, 25))

        # Box 3: Checkbox Options
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.auto_page = wx.CheckBox(panel, label='Automatic Page Calibration')
        self.auto_page.SetFont(font)
        hbox4.Add(self.auto_page)
        self.show_frames = wx.CheckBox(panel, label='Show Frames')
        self.show_frames.SetFont(font)
        hbox4.Add(self.show_frames, flag=wx.LEFT, border=10)
        vbox.Add(hbox4, flag=wx.LEFT, border=10)

        vbox.Add((-1, 25))

        # Box 4: Start and Close
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        btn1 = wx.Button(panel, label='Start', size=(70, 30))
        hbox5.Add(btn1)
        self.Bind(wx.EVT_BUTTON, self.StartProcessing, btn1)

        btn2 = wx.Button(panel, label='Close', size=(70, 30))
        self.Bind(wx.EVT_BUTTON, self.OnQuit, btn2)

        hbox5.Add(btn2, flag=wx.LEFT|wx.BOTTOM, border=5)
        vbox.Add(hbox5, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)

        panel.SetSizer(vbox)

    def OnQuit(self, e):
        self.Close()

    def StartProcessing(self, e):
        name = fd.askopenfilenames()
        print("---------------")
        print(self.auto_page)
        print("---------------")
        VideoTracker(name[0], './braille_files/B_2019 project FingerTracker.brf', auto_calibrate=False, auto_page_calibrate=self.auto_page.IsChecked(),
                     show_frame=self.show_frames.IsChecked(), paper_dims=(float(self.page_length.GetValue()), float(self.page_width.GetValue())))
        self.close()


def main():
    app = wx.App()
    gui = BrailleGUI(None, title='Finger Tracking')
    gui.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()