#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
title           :run_server.py.

description     :starts the server software
author          :Gareth Roberts, Department of Linguistics, University
                 of Pennsylvania
                 adapted for ZAS by Lisa Raithel
usage           :python run_server.py
notes           :Server.py requires installation of wxPython
python_version  :2.7.7
"""

from __future__ import unicode_literals

import sys
import datetime
import os

import Server

try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

# Allows messages to be sent between this software and the Server
# software itself
# from wx.lib.pubsub import setupkwargs
# from wx.lib.pubsub import pub
from pubsub import pub



#This was designed by Lisa to allow the experimenter to set all sorts of parameters.
#It would actually be better to have it automatically fill conditions based on what's needed


class Glbls():
    cwd = os.getcwd()
    nclnts = 0
    gui_show = 1
    # self.input_type = ""

    proper_path = os.path.join(cwd,"unnecessary","test_practice.csv")
    practice_path = os.path.join(cwd,"unnecessary","test_proper.csv")
    results_path = os.path.join(cwd,"results")
    images_path = os.path.join(cwd,"images")
    no_of_clicks = 15
    time = datetime.datetime.strftime(datetime.datetime.now(), "%b_%d_%y-%H_%M_%S")
    group_name = "group_" + time
    rand = False
    hard_mode = False
    swap = False
    time_per_round = 30




class SelectionPage(wx.Panel):
    """Window for setting up the server."""

    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.grid_sizer = wx.GridBagSizer(hgap=3, vgap=3)

        self.frame = parent

        startbutton = wx.Button(self, wx.ID_ANY, label="Start Server")

        self.warn_msg = ""
        self.warning = wx.StaticText(self, label=self.warn_msg)
        self.warning.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL,
                                     wx.BOLD))
        self.warning.SetForegroundColour(wx.RED)
        # This will listen out to a message from the Server that the
        # server has closed.
        pub.subscribe(self.finish_up, "serverclosed")
        self.all_items = []

        self._add_to_sizer_and_list(startbutton, (15, 1), (1, 2), wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.start_button_pressed, startbutton)
        self.Bind(wx.EVT_CLOSE, self.on_exit_app)

        self.SetSizer(self.grid_sizer)
        self.Center()
        self.grid_sizer.Fit(self)
        self.Layout()



    def _add_to_sizer_and_list(self, item, position, span=None, flag=None):
        self.all_items.append(item)

        if span is not None:
            if flag is not None:
                self.grid_sizer.Add(item, position, span, flag)
        else:
            self.grid_sizer.Add(item, position)

    def start_button_pressed(self,event):
        self.start_server()


    def start_server(self):

        self.Show(False)
        self.frame.Show(False)
        Server.Server(self,
                      Glbls.gui_show,
                      Glbls.nclnts,
                      Glbls.group_name,
                      Glbls.practice_path,
                      Glbls.proper_path,
                      Glbls.images_path,
                      Glbls.results_path,
                      Glbls.rand,
                      Glbls.hard_mode,
                      Glbls.swap,
                      Glbls.time_per_round,
                      Glbls.no_of_clicks)
        sys.exit()

    def finish_up(self, data):
        """Close server."""
        self.Destroy()

    def on_exit_app(self, event):
        """Exit the setup after reassurence."""
        quit_dialog = wx.MessageDialog(None,
                                        "Are you sure you want to quit setup?",
                                        "Quit?", wx.YES_NO)
        quitresult = quit_dialog.ShowModal()
        if quitresult == wx.ID_YES:
            quit_dialog.Destroy()
            self.Destroy()
        else:
            quit_dialog.Destroy()


    



class Setup(wx.Frame):
    """Window for setting up the server."""

    def __init__(self, parent, id, title):
        """Initialise the server setup.

        """

        no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER |
                                                wx.MAXIMIZE_BOX)
                                                # wx.RESIZE_BOX |
                                                

        wx.Frame.__init__(self, parent, id, title="Setup", style=no_resize,
                          size=(680, 480))
        # self.sizer = wx.GridBagSizer(hgap=3, vgap=3)
        self.fSizer = wx.BoxSizer(wx.VERTICAL)

        self.Show(False)
        selection_panel = SelectionPage(self)
        self.fSizer.Add(selection_panel, 1, wx.EXPAND)
        self.SetSizer(self.fSizer)
        self.Center()
        # selection_panel.start_server_externally()








class App(wx.App):
    """Main application to start the sever setup and the server."""

    def OnInit(self):
        """Standard wxPython initialisation function."""
        self.frame = Setup(parent=None, id=wx.ID_ANY, title="Server Setup")
        self.frame.Show(True)
        self.SetTopWindow(self.frame)

        return(True)


if __name__ == "__main__":
    app = App()
    # frame = Setup(None,wx.ID_ANY, 'Server setup')
    app.MainLoop()
