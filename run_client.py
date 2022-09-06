#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
title           :run_client.py.

description     :run_client.py is responsible for setting up and
                 starting the client for each participant of the
                 experiment
author          :originally Gareth Roberts, Department of Linguistics,
                 University of Pennsylvania,
                 modified by Lisa Raithel and Jon Stevens, ZAS, Berlin
usage           :python run_client.py
notes           :Client.py requires installation of wxPython
python_version  :2.7.7
"""

from __future__ import unicode_literals

import sys
import pickle
import Client

# make sure wxPython is installed
try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

# Allows messages to be sent between this software
# and the Client software itself
# from wx.lib.pubsub import setupkwargs
# from wx.lib.pubsub import pub
from pubsub import pub


class Setup(wx.Frame):
    """The client setup frame.
    Allows key input of file names/paths and selection of number
    of participants.
    """

    def __init__(self, parent, id, title):
        """Initialise the client setup.

        :param parent   :the parent of this frame
        :type parent    :None
        :param id       :the automatically picked id of the frame
        :type id        :int
        :param title    :the title of the frame
        :type title     :str
        """
        # initialise the frame
        wx.Frame.__init__(self, parent, id, title, size=(350, 200))
        # initialise panel and sizer
        panel = wx.Panel(self, wx.ID_ANY)
        self.panel = panel
        sizer = wx.GridBagSizer(hgap=3, vgap=3)

        # Checks to see if the last ip address was stored
        try:
            last_ip = pickle.load(open('temp_ip', "rb"))
        except(IOError):
            last_ip = ""

        # text entry for server ip
        server_ip_text = wx.StaticText(panel, wx.ID_ANY,
                                       label="Server IP address:")
        server_ip_box = wx.TextCtrl(panel, wx.ID_ANY, value=last_ip,
                                    size=(180, 30))
        self.server_ip_box = server_ip_box
        # text entry for participant name
        name_text = wx.StaticText(panel, wx.ID_ANY, label="Participant name:")
        name_box = wx.TextCtrl(panel, id=wx.ID_ANY,
                               size=(180, 30))
        self.name_box = name_box

        # dummy for warning messages
        self.warning = wx.StaticText(panel, wx.ID_ANY, label="")
        self.warning.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL,
                             wx.NORMAL))
        self.warning.SetForegroundColour(wx.RED)

        # if there is no last ip, set the focus to the ip box
        if last_ip != "":
            wx.CallAfter(self.name_box.SetFocus)

        # start button for starting the client
        startbutton = wx.Button(panel, wx.ID_ANY, label="Start Client")

        # listens out for a message from the Client frame that it's closed
        pub.subscribe(self.finish_up, "clientclosed")

        sizer.Add(server_ip_text, (1, 1))
        sizer.Add(server_ip_box, (1, 2), (1, 2), wx.EXPAND)
        sizer.Add(name_text, (2, 1))
        sizer.Add(self.name_box, (2, 2), (1, 2), wx.EXPAND)
        sizer.Add(self.warning, (3, 1))
        sizer.Add(startbutton, (4, 2), (1, 2), wx.EXPAND)

        startbutton.Bind(wx.EVT_BUTTON, self.on_start_button)

        # bind the exit event to the exit cross
        self.Bind(wx.EVT_CLOSE, self.on_exit_app)
        # bind the on key down event to both text boxes
        self.name_box.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        self.server_ip_box.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

        panel.SetSizer(sizer)
        # center the setup frame on the screen
        self.Center()
        # fitting does not look that good, so don't do it
        # sizer.Fit(self)

        # Do not allow participants to resize the window.
        self.SetSizeHints(self.GetSize().x, self.GetSize().y, self.GetSize().x,
                          self.GetSize().y)

    def start_client(self):
        """Start the client with a given or stored ip address."""
        # get ip address and participant name
        ip_address = self.server_ip_box.GetValue()
        name = self.name_box.GetValue()
        if ip_address != "" and name != "":
            pickle.dump(ip_address, open('temp_ip', 'wb'))
            self.Show(False)
            Client.Client(self, ip_address, name)
            sys.exit()
        else:
            if ip_address == "":
                self.warning.Hide()
                msg = "Please type in the IP address of the server, e.g. 'localhost'"
                self.warning.SetLabel(msg)
                self.warning.Show()
            else:
                self.warning.Hide()
                msg = "Please type in the participant's name, e.g. Peter'"
                self.warning.SetLabel(msg)
                self.warning.Show()

    def on_start_button(self, event):
        """Start the client when users presses 'start client'."""
        self.start_client()

    def on_key_down(self, event):
        """Allow to start the client when pressing enter."""
        key = event.GetKeyCode()
        if key == wx.WXK_RETURN:
            self.start_client()
        # proceed as before if enter was not pressed
        event.Skip()

    def finish_up(self, data):
        """Close client."""
        # kill everything connected to the client
        self.Destroy()

    def on_exit_app(self, event):
        """Exit the client setup after reassurence."""
        quit_dialoge = wx.MessageDialog(None,
                                        "Are you sure you want to quit the client setup?",
                                        "Quit?", wx.YES_NO)
        quitresult = quit_dialoge.ShowModal()
        if quitresult == wx.ID_YES:
            quit_dialoge.Destroy()
            self.Destroy()
        else:
            quit_dialoge.Destroy()


class App(wx.App):
    """The wx.Python application that starts the client gui."""

    def OnInit(self):
        """Initialise the client setup frame.

        Unfortunately this method's name has to be uppercase, because it's
        wxPython (does not work with lower case letters).
        """
        self.frame = Setup(parent=None, id=wx.ID_ANY, title='Client setup')
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

if __name__ == "__main__":
    app = App()
    app.MainLoop()
