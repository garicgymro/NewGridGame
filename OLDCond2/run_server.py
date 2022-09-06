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
import os.path

import Server

try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

# Allows messages to be sent between this software and the Server
# software itself
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
reload(sys)
sys.setdefaultencoding('utf8')


# class NextPage(wx.Panel):
#     """Window for setting up the server."""

#     def __init__(self, parent):
#         """Initialise the next page"""
#         wx.Panel.__init__(self, parent)
#         self.new_grid_sizer = wx.GridBagSizer(hgap=3, vgap=3)
#         self.frame = parent

#         startbutton = wx.Button(self, wx.ID_ANY, label="Start nothing")
#         next_button = wx.Button(self, wx.ID_ANY, label="next after next")
#         new_text = wx.StaticText(self, label="NEW NEW TEXT")
#         self.new_grid_sizer.Add(new_text, (5, 5))
#         self.new_grid_sizer.Add(startbutton, (1, 3))
#         self.new_grid_sizer.Add(next_button, (4, 6))

#         self.SetSizer(self.new_grid_sizer)
#         self.Center()
#         self.new_grid_sizer.Fit(self)
#         self.Layout()


class SelectionPage(wx.Panel):
    """Window for setting up the server."""

    def __init__(self, parent):
        """..."""
        self.nclnts = 0
        self.gui_show = 1
        # self.input_type = ""

        self.default_proper_parameters = "test_proper.csv"
        self.default_practice_parameters = "test_practice.csv"
        self.default_no_of_clicks = "15"
        self.default_time = "30"

        wx.Panel.__init__(self, parent)
        self.grid_sizer = wx.GridBagSizer(hgap=3, vgap=3)

        self.frame = parent

        startbutton = wx.Button(self, wx.ID_ANY, label="Start Server")
        # next_button = wx.Button(self, wx.ID_ANY, label="Next")

        self.no_of_participants_text = wx.StaticText(self,
                                                     label="Number of participants:")
        self.no_of_participants_text.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
                                             wx.NORMAL))
        self.button_2_part = wx.RadioButton(self, wx.ID_ANY,
                                            label="2 participants")
        self.button_2_part.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
                                   wx.NORMAL))
        self.button_2_part.SetValue(True)

        # self.button_4_part = wx.RadioButton(self, wx.ID_ANY,
        #                                     label="4 participants")
        # self.button_4_part.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
        #                            wx.NORMAL))

        self.group_name_text = wx.StaticText(self,
                                             label="Name of group:")
        self.group_name_box = wx.TextCtrl(self, wx.ID_ANY,
                                          size=(180, 30))
        self.group_name_text.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL))
        time = datetime.datetime.strftime(datetime.datetime.now(), "%H_%M_%S")
        label = "default: group_" + time

        self.group_name_hint = wx.StaticText(self,
                                             label=label)
        self.group_name_hint.SetFont(wx.Font(9.5, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL))

        no_of_possible_clicks = ["5", "10", "15", "20", "25", "30"]
        self.click_times = wx.ComboBox(self, -1, size=(120, -1),
                                       choices=no_of_possible_clicks,
                                       style=wx.CB_READONLY)
        self.click_times_text = wx.StaticText(self,
                                              label="Number of clicks per button:")
        self.click_times_text.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
                                              wx.NORMAL))
        default_no_of_clicks_string = ("default: " + self.default_no_of_clicks)
        self.click_times_hint = wx.StaticText(self,
                                              label=default_no_of_clicks_string)
        self.click_times_hint.SetFont(wx.Font(9.5, wx.DEFAULT, wx.NORMAL,
                                              wx.NORMAL))

        possible_times_per_round = ["5", "10", "15", "20", "25", "30"]
        self.time = wx.ComboBox(self, -1, size=(120, -1),
                                choices=possible_times_per_round,
                                style=wx.CB_READONLY)
        self.time_text = wx.StaticText(self, label="Time per round:")
        self.time_text.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
                                       wx.NORMAL))
        default_time_string = ("default: " + self.default_time + " seconds")
        self.time_hint = wx.StaticText(self, label=default_time_string)
        self.time_hint.SetFont(wx.Font(9.5, wx.DEFAULT, wx.NORMAL,
                                       wx.NORMAL))

        self.practice_rounds_box = wx.TextCtrl(self, wx.ID_ANY,
                                               size=(180, 30))
        self.practice_rounds_text = wx.StaticText(self,
                                                  label="Path to practice round parameters:")
        self.practice_rounds_text.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
                                          wx.NORMAL))
        default_practice_rounds_string = ("default: " +
                                          self.default_practice_parameters)
        self.practice_rounds_hint = wx.StaticText(self,
                                                  label=default_practice_rounds_string)
        self.practice_rounds_hint.SetFont(wx.Font(9.5, wx.DEFAULT, wx.NORMAL,
                                          wx.NORMAL))

        self.proper_rounds_box = wx.TextCtrl(self, wx.ID_ANY,
                                             size=(180, 30))
        self.proper_rounds_text = wx.StaticText(self,
                                                label="Path to normal round parameters:")
        self.proper_rounds_text.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
                                                wx.NORMAL))

        default_normal_rounds_string = "default: " + self.default_proper_parameters
        self.proper_rounds_hint = wx.StaticText(self,
                                                label=default_normal_rounds_string)
        self.proper_rounds_hint.SetFont(wx.Font(9.5, wx.DEFAULT, wx.NORMAL,
                                        wx.NORMAL))

        self.images_box = wx.TextCtrl(self, wx.ID_ANY,
                                      size=(180, 30))
        self.images_text = wx.StaticText(self,
                                         label="Path to images:")
        self.images_text.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
                                         wx.NORMAL))
        self.images_hint = wx.StaticText(self,
                                         label="default: images/")
        self.images_hint.SetFont(wx.Font(9.5, wx.DEFAULT, wx.NORMAL,
                                 wx.NORMAL))

        self.results_box = wx.TextCtrl(self, wx.ID_ANY,
                                       size=(180, 30))
        self.results_text = wx.StaticText(self,
                                          label="Path to results:")
        self.results_text.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
                                          wx.NORMAL))
        self.results_hint = wx.StaticText(self,
                                          label="default: results/")
        self.results_hint.SetFont(wx.Font(9.5, wx.DEFAULT, wx.NORMAL,
                                  wx.NORMAL))

        self.randomization = wx.CheckBox(self, wx.ID_ANY, label="Randomization")

        self.hard_mode = wx.CheckBox(self, wx.ID_ANY, label="Hard mode")

        self.swapping = wx.CheckBox(self, wx.ID_ANY, label="Swapping")
        
        self.randomization.SetValue(True)
        
        self.swapping.SetValue(True)
        
        self.time.SetValue(self.default_time)
        
        self.click_times.SetValue(self.default_no_of_clicks)

        # self.type_of_input_text = wx.StaticText(self,
        #                                         label="Answer generation:")
        # self.type_of_input_text.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
        #                                 wx.NORMAL))
        # self.button_dropdown = wx.RadioButton(self, wx.ID_ANY,
        #                                       label="dropdown",
        #                                       style=wx.RB_GROUP)
        # self.button_dropdown.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
        #                              wx.NORMAL))

        # self.button_text_entry = wx.RadioButton(self, wx.ID_ANY,
        #                                         label="manual entry")
        # self.button_text_entry.SetFont(wx.Font(10.5, wx.DEFAULT, wx.NORMAL,
        #                                wx.NORMAL))

        self.warn_msg = ""
        self.warning = wx.StaticText(self, label=self.warn_msg)
        self.warning.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL,
                                     wx.BOLD))
        self.warning.SetForegroundColour(wx.RED)
        # This will listen out to a message from the Server that the
        # server has closed.
        pub.subscribe(self.finish_up, "serverclosed")
        self.all_items = []

        self._add_to_sizer_and_list(self.no_of_participants_text, (1, 1))
        self._add_to_sizer_and_list(self.button_2_part, (1, 2))
        # self._add_to_sizer_and_list(self.button_4_part, (2, 2))

        # self._add_to_sizer_and_list(self.type_of_input_text, (4, 1))
        # self._add_to_sizer_and_list(self.button_dropdown, (4, 2))
        # self._add_to_sizer_and_list(self.button_text_entry, (5, 2))

        self._add_to_sizer_and_list(self.group_name_text, (4, 1))
        self._add_to_sizer_and_list(self.group_name_box, (4, 2))
        self._add_to_sizer_and_list(self.group_name_hint, (4, 4))

        self._add_to_sizer_and_list(self.click_times_text, (5, 1))
        self._add_to_sizer_and_list(self.click_times, (5, 2))
        self._add_to_sizer_and_list(self.click_times_hint, (5, 4))

        self._add_to_sizer_and_list(self.time_text, (6, 1))
        self._add_to_sizer_and_list(self.time, (6, 2))
        self._add_to_sizer_and_list(self.time_hint, (6, 4))

        self._add_to_sizer_and_list(self.practice_rounds_text, (7, 1))
        self._add_to_sizer_and_list(self.practice_rounds_box, (7, 2))
        self._add_to_sizer_and_list(self.practice_rounds_hint, (7, 4))

        self._add_to_sizer_and_list(self.proper_rounds_text, (8, 1))
        self._add_to_sizer_and_list(self.proper_rounds_box, (8, 2))
        self._add_to_sizer_and_list(self.proper_rounds_hint, (8, 4))

        self._add_to_sizer_and_list(self.images_text, (9, 1))
        self._add_to_sizer_and_list(self.images_box, (9, 2))
        self._add_to_sizer_and_list(self.images_hint, (9, 4))

        self._add_to_sizer_and_list(self.results_text, (10, 1))
        self._add_to_sizer_and_list(self.results_box, (10, 2))
        self._add_to_sizer_and_list(self.results_hint, (10, 4))

        self._add_to_sizer_and_list(self.randomization, (11, 2))

        self._add_to_sizer_and_list(self.hard_mode, (12, 2))

        self._add_to_sizer_and_list(self.swapping, (13, 2))

        self._add_to_sizer_and_list(self.warning, (14, 1))
        self._add_to_sizer_and_list(startbutton, (15, 1), (1, 2), wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.start_server, startbutton)
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

    def _get_no_of_participants(self):
        if self.button_2_part.GetValue():
            self.nclnts = 2
        # elif self.button_4_part.GetValue():
        #     self.nclnts = 4
        else:
            label = "Please choose the number of participants"
            self.warning.SetLabel(label)
            self.warning.Show()
            return False
        return True

    def _get_type_of_answer_generation(self):
        if self.button_dropdown.GetValue():
            self.input_type = "dropdown"
        elif self.button_text_entry.GetValue():
            self.input_type = "text entry"
        else:
            label = "Please choose sentence generation method"
            self.warning.SetLabel(label)
            self.warning.Show()
            return False
        return True

    def _get_group_name(self):
        time = datetime.datetime.strftime(datetime.datetime.now(), "%b_%d_%y-%H_%M_%S")
        try:
            self.group_name = self.group_name_box.GetValue()
            if self.group_name == "":
                self.group_name = "group_" + time

        except ValueError:
            self.group_name = "group_" + time

    def _get_path_to_practice(self):
        try:
            path = self.practice_rounds_box.GetValue()
            if path == "":
                path = self.default_practice_parameters
        except ValueError:
            path = self.default_practice_parameters
        if os.path.exists(path):
            self.practice_path = path
            return True
        else:
            label = "Please choose a correct path for the practice rounds file"
            self.warning.SetLabel(label)
            self.warning.Show()
            return False

    def _get_randomization(self):
        try:
            self.rand = self.randomization.GetValue()
        except ValueError:
            self.rand = False

    def _get_hard_mode(self):
        try:
            self.hm = self.hard_mode.GetValue()
        except ValueError:
            self.hm = False

    def _get_swapping(self):
        try:
            self.swap = self.swapping.GetValue()
        except ValueError:
            self.swap = False

    def _get_path_to_proper(self):
        try:
            path = self.proper_rounds_box.GetValue()
            if path == "":
                path = self.default_proper_parameters
        except ValueError:
            path = self.default_proper_parameters
        if os.path.exists(path):
            self.proper_path = path
            return True
        else:
            label = "Please choose a correct path for the proper rounds file"
            self.warning.SetLabel(label)
            self.warning.Show()
            return False

    def _get_path_to_images(self):
        try:
            path = self.images_box.GetValue()
            if path == "":
                path = "images"
        except ValueError:
            path = "images"
        if os.path.exists(path):
            if os.path.isdir(path):
                self.images_path = path
                return True

            label = "Please choose a correct path for the image directory"
            self.warning.SetLabel(label)
            self.warning.Show()

            return False
        else:
            label = "Please choose a correct path for the image directory file"
            self.warning.SetLabel(label)
            self.warning.Show()
            return False

    def _get_no_of_clicks_per_button(self):
        try:
            self.no_of_clicks = int(self.click_times.GetValue())
        except ValueError:
            self.no_of_clicks = int(self.default_no_of_clicks)

    def _get_time_per_round(self):
        print "getting time per round"
        try:
            self.time_per_round = int(self.time.GetValue())
        except ValueError:
            self.time_per_round = int(self.default_time)

    def _get_path_to_results(self):
        try:
            self.results_path = self.results_box.GetValue()
            if self.results_path == "":
                self.results_path = "results"
        except ValueError:
            self.results_path = "results"

    def start_server(self, event):
        """Start the server if all requirements are fulfilled."""
        self._get_group_name()
        # if this path does not exist, it is newly created
        self._get_path_to_results()
        # set the randomization parameter to True or False
        self._get_randomization()
        # set mode (hard mode clears the grid if time runs out)
        self._get_hard_mode()
        # set role swapping
        self._get_swapping()
        # get time per round
        self._get_time_per_round()
        # get number of clicks per button
        self._get_no_of_clicks_per_button()
        # check for all paths if they are correct
        if (self._get_no_of_participants()):
            if(self._get_path_to_proper()):
                if(self._get_path_to_practice()):
                    if(self._get_path_to_images()):
                        # This window hovers invisible in the
                        # background until the Server is closed.
                        self.Show(False)
                        self.frame.Show(False)
                        Server.Server(self,
                                      self.gui_show,
                                      self.nclnts,
                                      self.group_name,
                                      self.practice_path,
                                      self.proper_path,
                                      self.images_path,
                                      self.results_path,
                                      self.rand,
                                      self.hm,
                                      self.swap,
                                      self.time_per_round,
                                      self.no_of_clicks)
                        sys.exit()

    def finish_up(self, data):
        """Close server."""
        self.Destroy()

    def on_exit_app(self, event):
        """Exit the setup after reassurence."""
        quit_dialoge = wx.MessageDialog(None,
                                        "Are you sure you want to quit the setup?",
                                        "Quit?", wx.YES_NO)
        quitresult = quit_dialoge.ShowModal()
        if quitresult == wx.ID_YES:
            quit_dialoge.Destroy()
            self.Destroy()
        else:
            quit_dialoge.Destroy()


class Setup(wx.Frame):
    """Window for setting up the server."""

    def __init__(self, parent, id, title):
        """Initialise the server setup.

        Some basic parameters: number of clients, number of practice
        rounds, should the Server GUI be visible
        """

        self.default_proper_parameters = "test_proper.csv"
        self.default_practice_parameters = "test_practice.csv"

        self.default_no_of_clicks = "5"
        self.default_time = "5"

        no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER |
                                                wx.RESIZE_BOX |
                                                wx.MAXIMIZE_BOX)

        wx.Frame.__init__(self, parent, id, title="Setup", style=no_resize,
                          size=(680, 480))
        # self.sizer = wx.GridBagSizer(hgap=3, vgap=3)
        self.fSizer = wx.BoxSizer(wx.VERTICAL)

        self.Show(False)
        selection_panel = SelectionPage(self)
        self.fSizer.Add(selection_panel, 1, wx.EXPAND)
        self.SetSizer(self.fSizer)
        self.Center()


class App(wx.App):
    """Main application to start the sever setup and the server."""

    def OnInit(self):
        """Standard wxPython initialisation function."""
        self.frame = Setup(parent=None, id=wx.ID_ANY, title="Server Setup")
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


if __name__ == "__main__":
    app = App()
    # frame = Setup(None,wx.ID_ANY, 'Server setup')
    app.MainLoop()
