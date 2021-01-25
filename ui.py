#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Code to make a GUI to run the RiceBraille project using wxPython.

Code is adapted from Jan Bodnar's ZetCode wxPython tutorial.
sample code author: Jan Bodnar
website: www.zetcode.com
last modified: April 2018
"""

import wx
from VideoTracker import VideoTracker

# inherits from wx.Frame, a standard container widget
class BrailleGUI(wx.Frame):

    def __init__(self, parent, title):
        # initialize window params
        super(BrailleGUI, self).__init__(parent, title=title)
        self.auto_finger = 0
        self.auto_page = 0
        self.char_track = 0
        self.show_frames = 0
        self.page_length = 0
        self.page_width = 0
        self.brfFile = None
        self.videoFile = None

        self.InitUI()
        self.Centre()

    def InitUI(self):
        
        panel = wx.Panel(self)

        # obtain system font
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        # we have one vertical sizer, and then a bunch of horizontal sizers inside that vertical sizer
        vbox = wx.BoxSizer(wx.VERTICAL)

        ### SECTION 1: CORE AUTOMATIC FEATURES
        # Instructions
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        st0 = wx.StaticText(panel, label='Select core automatic features to enable:')
        st0.SetFont(font)
        hbox0.Add(st0, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=8)
        vbox.Add(hbox0)

        # Automatic Finger Calibration
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Enable Automatic Finger Calibration:')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=8)
        self.auto_finger = wx.CheckBox(panel)
        hbox1.Add(self.auto_finger, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=8, proportion=1)
        vbox.Add(hbox1)

        # box.Add can insert not only widgets, but also empty space
        vbox.Add((-1, 5))

        # Automatic Page Calibration
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Enable Automatic Page Calibration:')
        st2.SetFont(font)
        hbox2.Add(st2, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=8)
        self.auto_page = wx.CheckBox(panel)
        self.auto_page.SetValue(True)
        hbox2.Add(self.auto_page, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=8, proportion=1)
        vbox.Add(hbox2)

        vbox.Add((-1, 25))

        ### SECTION 2: SUPPLEMENTARY FEATURES
        # Instructions
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, label='If character tracking is desired, upload a .brf file:')
        st3.SetFont(font)
        hbox3.Add(st3, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=8)
        vbox.Add(hbox3)

        # Character Tracking
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        st4 = wx.StaticText(panel, label='Upload .brf file:')
        st4.SetFont(font)
        hbox4.Add(st4, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=8)
        btn0 = wx.Button(panel, label='Choose file', size=(70, 30))
        hbox4.Add(btn0)
        self.Bind(wx.EVT_BUTTON, self.OnOpenBrf, btn0)
        vbox.Add(hbox4)

        vbox.Add((-1, 25))

        ### SECTION 3: Additional Options
        

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

    def OnOpenBrf(self, event):
        """
        Event handler to take a .brf file input
        code from: https://wxpython.org/Phoenix/docs/html/wx.FileDialog.html 
        """
        with wx.FileDialog(self, "Open .brf file", wildcard=".brf files (*.brf)|*.brf", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Save file path given
            self.brfFile = fileDialog.GetPath()

    def OnQuit(self, event):
        """
        Event handler to quit software
        """
        self.Close()

    def StartProcessing(self, event):
        """
        Event handler to start processing video
        """
        with wx.FileDialog(self, "Open .brf file", wildcard=".brf files (*.brf)|*.brf", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Save file path given
            self.brfFile = fileDialog.GetPath()

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