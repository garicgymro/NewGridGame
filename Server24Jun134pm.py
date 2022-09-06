#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Contains the classes Player, Server, Srvr, Gui and ListenForClients.

title           :Server.py
description     :Server software
author          :Gareth Roberts, Department of Linguistics,
                 University of Pennsylvania
                 Adapted for ZAS Berlin by Lisa Raithel and Jon Stevens
                 Adapted for Grid Game by Inthat Boonpongmanee
usage           :pythonw run_server.py
notes           :Requires installation of wxPython
python_version  :3.9.12
"""

from __future__ import unicode_literals

import codecs
import collections
import csv
import datetime
import json
import os
import random
import re
import socket
import sys
import threading
import time

from parameter_reader import Parameters

try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

# you need this one to shut down the server and clients correctly
# from wx.lib.pubsub import pub
# from wx.lib.pubsub import setupkwargs
from pubsub import pub 
# from pubsub import setupkwargs

import wx.richtext as rt

# needed for dict
import collections


class Glbl():

    referent = ""
    currentGuess = ""
    full_message_dictionary = {}
    #collections.defaultdict(list)


    # Referent list for open set implementation
    # totalRefList = ["Dog", "Pet", "Animal", "Ice cream", "Dessert", "Daisy", "Flower", "Plant", "Apple", "Fruit",
    #                      "Book", "Novel"]


    dogList = ["Dog", "Pet", "Animal"]
    foodList = ["Ice cream", "Dessert"]
    plantList = ["Daisy", "Flower", "plant"] #shouldn't plant be included?
    fruitList = ["Apple", "Fruit"]
    objectList = ["Book", "Novel"]

    totalRefList = dogList + foodList + plantList + fruitList + objectList



    # USED FOR TESTING referent lists, complexity substitution -
    # uncomment all instance of testRefList to insert your own list of referents
    testRefList = ["Dog", "Dog", "Dog", "Dog",
                   "Dog", "Dog", "Dog", "Dog"]
    round = 0 # used to prevent list indexing errors when testing

    # Populated by getRefList() method
    sentRefList = []
    # shuffledTotalList = random.shuffle(totalRefList)

    # String version of refList sent through server messages converted from sentRefList
    stringRefList = ""






    conditions = [{"substitute":(0.1, 0.8),"noise": None},
    {"substitute":(0.8,0.8),"noise": (0.1, 0.25)},
    {"substitute":(0.3,0.8),"noise": (0.1, 0.25)}
    ]

    condition_index = 0

    #First noise threshold now controle whether noise occurs in a given round
    #Second threshold applies per cell

    # [(0.8,0.8),(0.1, 0.3)],
    # [(0.3, 0.8), (0.1, 0.3)]
    # ]

   
    # experiment1 = True
    # experiment1Param = [(0.1, 0.8),()]
    # # high complexity, low/high noise
    # experiment2 = False
    # experiment2Param = [(0.8,0.8),(0.1, 0.3)]
    # # low/high complexity, low/high noise
    # experiment3 = False
    # experiment3Param = [(0.3, 0.8), (0.1, 0.3)]







    #Complexity substitution parameters - max unique referents substituted, number of times substituted,
    # minimum interval between substitutions.
    # complexityParam = [1, 1, 1]c
    #Better as a dictionary!
    complexityParam = {"max_unique":1, "num_substitutions":1, "min_interval":1 }

    # complexityTracker is a dictionary of lists
    # key : value
    # referent : (# subs, interval between last)
    complexityTracker = collections.defaultdict(list)

    substitution_noise_combine = False #Can noise apply on rounds where 
    substitution_round = False
    substitutionCount = 0


class Player():
    """Class for the player instance."""

    def __init__(self, clnt, gui, srvr):
        """The internal representation of a player.

        Connects GUI, server and clients and saves
        the player's real and fake name.

        :param clnt:
        :type clnt:
        :param gui:
        :type gui:
        :param srvr:
        :type svrv:
        """
        self.clnt = clnt
        self.gui = gui
        self.srvr = srvr
        self.realname = "?"
        self.fakename = "?"
        # for what do I need those two?
        self.action = "?"
        self.index = 9999
        self.partner = None


class Gui(wx.Frame):
    """..."""

    def __init__(self, parent, id, title, gui_show, nclnts,
                 practice_rounds_config, proper_rounds_config, csv_header,
                 group_name, images_path, results_path,
                 randomization, hard_mode, swapping, time_per_round, no_of_clicks):
        """..."""
        self.bufsize = 4096
        # host = socket.gethostname()
        self.host = ""
        self.port = 5000


        #These settings are a legacy of the old experiment. They're set in run_server.py, which sets these parameters when it calls Server.py
        self.randomization = randomization
        self.hard_mode = hard_mode
        self.swapping = swapping
        self.time_per_round = time_per_round
        self.no_of_clicks = no_of_clicks
        # print("self.randomization = ", self.randomization)
        # print("self.hard_mode = ", self.hard_mode)
        # print("time per round = ", self.time_per_round)
        # print("no_of_clicks per button = ", self.no_of_clicks)

        self.images_path = images_path

        self.num_practice_rounds = len(practice_rounds_config)
        self.practice_rounds_config = practice_rounds_config
        self.current_practice_config = {}
        # This must be the same as in the Server script
        self.server_end_marker = "!!!%%%&&&!!!"
        self.allconnected = 0
        self.guilock = threading.Lock()
        self.results_dir = results_path
        print("self.results_dir = ", self.results_dir)
        # is the results directory does not exist already, build it
        if not os.path.exists(self.results_dir):
            print("creating results directory")
            os.makedirs(self.results_dir)

        #threads allow processes to run in parallel
        self.threads = []
        self.realnames = []
        self.header = csv_header
        self.nclnts = nclnts
        self.proband_group_name = group_name        
        
        # get parameters from parameter file:
        self.parameters_for_proper_rounds = proper_rounds_config
        
        file_name = ("results_group_" + self.proband_group_name + ".txt")
        file_path = os.path.join(self.results_dir,file_name)
        f = open(file_path,"a")
        f.write("Parameters:\n")
        parameter_line = ("Swapping: " + str(self.swapping)
                          + "\nRandomization: " + str(self.randomization)
                          + "\nTime per round: " + str(self.time_per_round)
                          + "\nHard mode: " + str(self.hard_mode)
                          + "\nNumber of clicks: " + str(self.no_of_clicks)
                          + "\nGradual cell filling: False\n")
        f.write(parameter_line)
        f.close()
        
        self.num_of_rounds = len(self.parameters_for_proper_rounds)

        # change this if you want 2 or 4 participants
        if self.nclnts == 2:
            self.fakenames = ["thor", "freya"]
            self.listener = None
            self.speaker = None
            self.roles = ["listener", "speaker"]
            self.key = ""

        else:
            self.fakenames = ["thor", "freya", "loki", "odin"]
            self.listener_1 = None
            self.listener_2 = None
            self.speaker_1 = None
            self.speaker_2 = None
            self.roles = ["listener_1", "speaker_1", "listener_2", "speaker_2"]
            self.key_1 = ""
            self.key_2 = ""

        # self.speaker_no = 30
        # self.listener_no = 60

        self.survey_answers = {}
        self.players = {}
        self.playerlist = []
        self.gui_show = gui_show
        self.finish = 0
        self.timestamp_format = "%b-%d-%y; %H:%M:%S "
        self.players_read_instructions = []
        self.players_finished_buttons = []

        self.players_completed_survey = []
        self.players_finished = []
        self.paused = 0
        self.players_ready = []
        self.player_count = 0
        self.clients_closed = []

        self.player_finder = {}
        self.scores = {}
        self.image_1 = ""
        self.image_2 = ""

        self.overall_rounds = 0
        self.practice_round = 0
        self.practice_over = 0
        self.round = 0

        wx.Frame.__init__(self, parent, id, title)

        self.StageTimer = wx.Timer(self)

        panel = wx.Panel(self, wx.ID_ANY)
        self.panel = panel
        sizer = wx.GridBagSizer()

        message_window = rt.RichTextCtrl(panel, id=wx.ID_ANY,
                                         style=wx.TE_READONLY, size=(600, 400))
        quit_button = wx.Button(panel, wx.ID_ANY, label="Quit")
        hide_button = wx.Button(panel, wx.ID_ANY, label="Hide Server")
        # new_round_button = wx.Button(panel, wx.ID_ANY, label="Force new Round")

        self.message_window = message_window
        self.quit_button = quit_button
        self.hide_button = hide_button

        sizer.Add(self.message_window, (0, 0), span=(1, 2))
        sizer.Add(quit_button, (1, 0))
        sizer.Add(hide_button, (1, 1))
        # sizer.Add(new_round_button, (1, 1))

        # pause_button = wx.Button(panel, wx.ID_ANY, label="Pause")
        # self.pause_button = pause_button
        # sizer.Add(self.pause_button, (2, 1))

        panel.SetSizer(sizer)
        sizer.Fit(self)
        self.SetSizeHints(self.GetSize().x, self.GetSize().y, self.GetSize().x,
                          self.GetSize().y)
        self.Bind(wx.EVT_CLOSE, self.on_exit_app)
        self.Bind(wx.EVT_BUTTON, self.on_quit_button, quit_button)
        self.Bind(wx.EVT_BUTTON, self.on_hide_button, hide_button)
        # self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_TIMER, self.on_stage_timer, self.StageTimer)
        # self.Bind(wx.EVT_BUTTON, self.on_force_new_round, new_round_button)

        self.Show(True)
        self.threads.append(ListenForClients(self, self.host, self.port))
        for thread in self.threads:
            # so it'll stop when everything else does
            thread.daemon = True
            thread.start()

    def final_results_read(self):
        """..."""
        print("all clients closed")
        self.finish = 1
        msg = "Closing at Server end"
        pub.sendMessage("serverclosed", data=msg)
        # self.guilock.acquire()
        # for player in self.playerlist:
        #     killmessage = self.encode('9999KILL9999')
        #     player.clnt.send(killmessage)
        #     player.clnt.close()
        # self.Destroy()
        sys.exit()
        # self.guilock.release()

    # For messages that should appear on the server window.
    def screen_message(self, msg):
        """..."""
        self.message_window.WriteText(msg)
        self.message_window.WriteText("\n")
        end = self.message_window.GetCaretPosition()
        self.message_window.ShowPosition(end)

    def write_survey_to_results(self):
        """Write the results of the survey to a separate file."""
        self.guilock.acquire()
        survey_file_name = ("survey_results_group_" + self.proband_group_name +
                            ".txt")
        survey_file_path = self.results_dir + "/" + survey_file_name
        if os.path.isfile(survey_file_path):
            time = datetime.datetime.strftime(datetime.datetime.now(), "%b_%d_%y-%H_%M_%S")
            
            self.proband_group_name = "group_" + time
            survey_file_name = ("survey_results_group_" + self.proband_group_name +
                                ".txt")
            survey_file_path = self.results_dir + "/" + survey_file_name
        # with codecs.open(survey_file_path, "w") as write_handle:
        with open(survey_file_path, "w") as write_handle:
            intro = ("Survey answers for participant group " +
                     self.proband_group_name + "\n\n")
            write_handle.write(intro)
            for player, answers in self.survey_answers.iteritems():
                parts = answers.split(",")
                stripped = []
                for answer in parts:
                    stripped.append(answer.strip())
                answer_string = "\n".join(stripped)
                player = player + ":\n"

                try:
                    write_handle.write(player.encode('utf-8'))
                    write_handle.write(answer_string.encode('utf-8'))

                except:
                    tm = time.strftime(self.timestamp_format)
                    error_msg = tm + ": MISSING DATA: COULDN'T WRITE DATA"
                    write_handle.write(error_msg)
                write_handle.write("\n\n")
        self.guilock.release()

    def write_message_to_file(self, msg):
        self.guilock.acquire()
        time = datetime.datetime.strftime(datetime.datetime.now(), "%b_%d_%y-%H_%M_%S")
        file_name = ("results_group_" + self.proband_group_name + ".txt")
        file_path = os.path.join(self.results_dir,file_name)
        # with codecs.open(file_path, "a") as results_file:
        #     to_append = time + " | " + msg + "\n"
        #     results_file.write(to_append.encode('utf-8'))
        with open(file_path, "a") as results_file:
            to_append = time + " | " + msg + "\n"
            results_file.write(to_append)
            
        self.guilock.release()

    def encode(self, item):
        """Encode a message that is to be sent to the client(s)."""
        #This is important for transmission purposes. 
        #Because the channel is essentially open, the end marker ensures distinct messages don't run into each other.
        #(Or rather, if they do, it allows us to distinguish them.)

        encoded_item = item.encode("utf-8") + self.server_end_marker.encode("utf-8")
        return(encoded_item)


    def on_exit_app(self, event):
        """Quit the GUI after reassurance."""
        if self.allconnected == 1:
            quit_dialogue = wx.MessageDialog(None, "Are you sure you want to quit the GUI?", "Quit?",
                                            wx.YES_NO)
            quitresult = quit_dialogue.ShowModal()
            if quitresult == wx.ID_YES:
                quit_dialogue.Destroy()
                self.finish = 1
                msg = "Closing at Server end"
                pub.sendMessage("serverclosed", data=msg)
                # if self.playerlist != []:
                killmessage = self.encode('9999KILL9999')
                for player in self.playerlist:
                    player.clnt.send(killmessage)
                    player.clnt.close()
                self.Destroy()
            else:
                quit_dialogue.Destroy()
        else:
            quit_dialogue = wx.MessageDialog(None, "Are you sure you want to quit the GUI?", "Quit?",
                                            wx.YES_NO)
            quitresult = quit_dialogue.ShowModal()
            if quitresult == wx.ID_YES:
                quit_dialogue.Destroy()

                self.Destroy()
                sys.exit()
            else:
                quit_dialogue.Destroy()

    def on_quit_button(self, event):
        """Quit the GUI after reassurence."""
        if self.allconnected == 1:
            quit_dialogue = wx.MessageDialog(None, "Are you sure you want to quit the GUI?", "Quit?",
                                            wx.YES_NO)
            quitresult = quit_dialogue.ShowModal()
            if quitresult == wx.ID_YES:
                quit_dialogue.Destroy()
                self.finish = 1
                msg = "Closing at Server end"
                #pub.sendMessage("serverclosed", data=msg)
                # if self.playerlist != []:
                killmessage = self.encode('9999KILL9999')
                for player in self.playerlist:
                    player.clnt.send(killmessage)
                    player.clnt.close()
                self.Destroy()
                sys.exit()
            else:
                quit_dialogue.Destroy()
        else:
            quit_dialogue = wx.MessageDialog(None, "Are you sure you want to quit the GUI?", "Quit?",
                                            wx.YES_NO)
            quitresult = quit_dialogue.ShowModal()
            if quitresult == wx.ID_YES:
                quit_dialogue.Destroy()

                self.Destroy()
                sys.exit()
            else:
                quit_dialogue.Destroy()

    def on_pause_button(self, event):
        """..."""
        if self.allconnected == 1 and self.paused == 0:
            quit_dialogue = wx.MessageDialog(None, "", "Pause? Are you sure?",
                                            wx.YES_NO)
            quitresult = quit_dialogue.ShowModal()
            if quitresult == wx.ID_YES:
                quit_dialogue.Destroy()
                self.paused = 1
                self.pause_button.SetLabel("Unpause")
                tm = time.strftime(self.timestamp_format)
                msg = "Pause button pressed."
            else:
                quit_dialogue.Destroy()
                pass
        elif self.allconnected == 1 and self.paused == 1:
            self.paused = 0
            self.pause_button.SetLabel("Pause")
            tm = time.strftime(self.timestamp_format)
            msg = "Game unpaused"
            self.OnNewStage()
        else:
            pass




    #This allows the server window to be hidden if it's running on the same computer as a client
    def on_hide_button(self, event):
        """..."""
        self.gui_show = 0
        self.Show(False)

    def on_reveal(self):
        """..."""
        self.gui_show = 1
        self.Show(True)
        end = self.message_window.GetCaretPosition()
        self.message_window.ShowPosition(end)

    # def on_force_new_round(self, event):
    #     """..."""
    #     self.force_new_round()

    # def force_new_round(self):
    #     """..."""
    #     self.on_new_round()

    def on_stage_timer(self, event):
        """..."""
        try:
            self.StageTimer.Stop()
        except:
            pass
        self.on_new_round()

    def finish_game(self):
        """..."""
        for player in self.playerlist:
            message = "9999GAMEOVER9999"
            encoded_message = self.encode(message)
            player.clnt.send(encoded_message)

    def practice_rounds_over(self):
        """..."""
        for player in self.scores:
            self.scores[player] = 0
        self.practice_over = 1
        for player in self.playerlist:
            message = self.encode("9999ALLPRACTICEOVER@_@9999")
            player.clnt.send(message)

    def on_new_round(self):
        """Start a new round.
        """
        self.images = []
        # print("on_new_round has been called")

        # Translates the RefList to a string with referents separated by ", "
        refList = Srvr.getRefList(self)
        # print("result of getRefList(self) (a list)", refList)

        # USED FOR TESTING
        # refList = Glbl.testRefList

        Glbl.stringRefList = ", ".join(str(x) for x in refList)
        # print("Check to see if getRefList converts to string properly", Glbl.stringRefList)
        # starting proper rounds
        if self.paused == 0 and self.practice_over == 1:
            print("IN PROPER ROUNDS")
            if self.round < self.num_of_rounds:
                print("\n\n\nFINISHED ROUND" + str(self.round) + "\n\n\n")
                if self.round > 0:
                    m = "Round " + str(self.round) + " finished.\n"
                    wx.CallAfter(self.screen_message, m)
                self.round += 1

                image_pair = [
                self.parameters_for_proper_rounds[self.round]["image_1"],
                self.parameters_for_proper_rounds[self.round]["image_2"]
                ]
                image_pair = random.sample(image_pair, len(image_pair))
                self.image_1 = image_pair[0]
                self.image_2 = image_pair[1]

                for participant in self.playerlist:
                    # Ignore image_1, image_2


                    message = "9999ALLPROPERROUND" + "@" + self.image_1 + "=" + self.image_2 + "@" + \
                              Glbl.stringRefList + "9999"
                    # print("proper round on_new_round() -> starting message", message)
                    encoded_message = self.encode(message)
                    participant.clnt.send(encoded_message)

            else:
                self.finish_game()

        # game paused, but practice rounds are not over
        elif self.paused == 0 and self.practice_over == 0:
            print("IN PRACTICE ROUNDS")
            self.practice_round += 1
            if self.practice_round > self.num_practice_rounds:
                self.practice_rounds_over()
            else:
                image_pair = [
                self.practice_rounds_config[self.practice_round]["image_1"],
                self.practice_rounds_config[self.practice_round]["image_2"]
                ]
                image_pair = random.sample(image_pair, len(image_pair))
                self.image_1 = image_pair[0]
                self.image_2 = image_pair[1]

                for participant in self.playerlist:

                    message = "9999ALLPRACTICEROUND" + "@" + self.image_1 + "=" + self.image_2 + "@" \
                              + Glbl.stringRefList + "9999"
                    # print("practice round on_new_round() -> starting message", message)
                    encoded_message = self.encode(message)
                    participant.clnt.send(encoded_message)


    def all_ready(self):
        """..."""
        for player in self.playerlist:
            if self.practice_over == 1:
                pass
            else:
                message = self.encode("9999WHATISTHISFOR9999")
                player.clnt.send(message)
        self.on_new_round()





    def initial_setup(self):
        """..."""
        random.shuffle(self.fakenames)

        self.playerlist[0].partner = self.playerlist[1]
        self.playerlist[1].partner = self.playerlist[0]


        for i in range(len(self.playerlist)):
            self.playerlist[i].fakename = self.fakenames[i]
            self.player_finder[self.fakenames[i]] = self.playerlist[i]
            # self.scores[self.fakenames[i]] = 0

        for player in self.playerlist:
            Glbl.full_message_dictionary[str(player)] = collections.defaultdict(list)

            msg = "9999WELCOME" + str(self.randomization) + "@" + str(self.hard_mode) + "9999"
            message = self.encode(msg)
            player.clnt.send(message)



    def setup_instructions(self):
        """..."""
        random.shuffle(self.fakenames)
        for i in range(len(self.playerlist)):
            self.playerlist[i].fakename = self.fakenames[i]
            self.player_finder[self.fakenames[i]] = self.playerlist[i]
            self.scores[self.fakenames[i]] = 0
        for player in self.playerlist:
            message = "9999ALLINSTRUCTIONS@@9999"
            encoded_message = self.encode(message)
            player.clnt.send(encoded_message)

    def send_words_to_listener(self, words, player_index):
        """..."""
        encoded_message = self.encode(words)
        if self.nclnts == 2:
            self.listener.clnt.send(encoded_message)
        else:
            if player_index == 1:
                self.listener_1.clnt.send(encoded_message)
            else:
                self.listener_2.clnt.send(encoded_message)


# Takes in data from clients and directs
# it to the right places
class Srvr(threading.Thread):
    """..."""

    data = ''
    dlock = threading.Lock()

    def __init__(self, clntsock, gui):
        """..."""

        # Moved to Glbl class
        # self.referent = 'empty';
        # self.currentGuess = '';


        threading.Thread.__init__(self)
        self.gui = gui
        self.myclntsock = clntsock
        self.data = Srvr.data
        self.srvr_msg = re.compile(r'9999.*9999\s')
        self.clnt_msg = re.compile(r'6666.*6666\s')
        self.info_msg = re.compile(r'6666INFO.*6666')
        self.listener_msg = re.compile(r'.*LISTENERDONE@(.*)@(.*)@.*')
        self.pic_chosen_msg = re.compile(r"6666PIC(.*)@(.*)@.*")

        # *** Message contains
        # *** This is sent by
        # group 3 contains correctReferent
        self.listener_ref_chosen_msg = re.compile(r"6666GUESS(.*)@(.*)@(.*)@.*")

        # *** Message containing coordinates, sender name, correct referent (in that order). ***
        # *** This is sent by the speaker to the server. The server extracts the coords and stores it in the dict ***
        self.coord_msg = re.compile(r"6666COORD(.*)@(.*)@(.*)@.*")


        # *** Complexity substitution fields ***
        # This is a dictionary containing referent:coordinate mappings.
        # After the coordinates for each referent are received,
        # they are appended onto the end of the list in the values.




        self.practice_msg = re.compile(r'6666READYFORNEXTPRACTICE(.*)@(.*)6666')
        self.instructions_read_msg = re.compile(r".*INSTRUCTIONSREAD.*")
        self.finished_buttons_msg = re.compile(r".*FINISHEDBUTTONS.*")
        self.close_msg = re.compile(r".*CLOSED.*")
        self.qa_msg = re.compile(r'6666QA(.*)6666(?!\s)')
        self.player = None
        self.buffer = []


        # I want this to store key:value -> referent: tuple (coords, complexity, correct)

        # Storing scores for each image

    def decode_strings(self, string):
        """Decode a string to utf-8."""
        return(string.decode("utf-8"))

    def recv_end(self, the_socket):
        """..."""
        end = self.gui.server_end_marker
        total_data = self.buffer
        messages = []
        data = ''
        while True:
            raw_data = the_socket.recv(self.gui.bufsize)
            data = self.decode_strings(raw_data)

            if end in data:
                # msg_part = data[:data.find(end)].decode()
                total_data.append(data[:data.find(end)])
                messages.append(total_data)
                total_data = []
                self.buffer = []
                message_length = len(end) + len(data[:data.find(end)])
                if message_length < len(data):
                    leftover = data[message_length:]
                    while True:
                        if end in leftover:
                            total_data.append(leftover[:leftover.find(end)])
                            messages.append(total_data)
                            total_data = []
                            message_length = (len(end) +
                                              len(leftover[:leftover.find(end)]))
                            if len(leftover) == message_length:
                                break
                            else:
                                leftover = leftover[message_length:]
                        else:
                            self.buffer.append(leftover)
                            break

                break
            total_data.append(data)
            if len(total_data) > 1:
                # check if end_of_data was split
                last_pair = total_data[-2] + total_data[-1]
                if end in last_pair:
                    total_data[-2] = last_pair[:last_pair.find(end)]
                    total_data.pop()
                    break
        messages2return = []
        # print(messages)
        for msg in messages:
            # print(msg)
            messages2return.append(''.join(msg))

        return(messages2return)

    # Check if a Srvr object is made and where run is called
    def run(self):
        # print("Now running")
        """..."""
        def establish_client_list():
            print("establishing client list...")
            """..."""
            name_message = "Participant names: "
            counter = 0


            self.gui.speaker = self.gui.playerlist[0]
            self.gui.listener = self.gui.playerlist[1]

            for i in range(0, len(self.gui.playerlist)):
                self.gui.playerlist[i].index = i
                counter += 1
                name_message += str(i)
                name_message += ":"
                name_message += str(self.gui.playerlist[i].realname)
                if counter % 4 == 0 and counter != len(self.gui.playerlist):
                    name_message += "\n"
                else:
                    name_message += " "

            for i in range(len(self.gui.playerlist)):
                begin_message = self.gui.encode("9999BEGIN" + str(i) + "@" +
                                                self.gui.images_path + "@" + str(self.gui.no_of_clicks) +
                                                "@" + str(self.gui.time_per_round) + "@" + str(self.gui.swapping) + "9999")
                self.gui.playerlist[i].clnt.send(begin_message)
            wx.CallAfter(self.gui.initial_setup)

        while 1:
            # indata_list = self.recv_end(self.myclntsock)
            try:
                indata_list = self.recv_end(self.myclntsock)
            except:
                print('Connection closed due to socket exception. No longer receiving data.')
                # sys.exit()
                break
            for indata in indata_list:
                Srvr.dlock.acquire()
                self.data = indata
                # print("self.data = ", self.data)
                self.gui.write_message_to_file(self.data)
                if (re.match(self.srvr_msg, self.data) or
                   re.match(self.clnt_msg, self.data)):
                    msg = 'Participant ' + str(self.player.index) + ' knows too much'

                elif self.data == '6666NEXTROUND6666':
                    self.gui.on_new_round()

                elif self.data == '6666KILL6666':
                    # msg = "Closing at Server end"
                    # pub.sendMessage("serverclosed", data=msg)

                    Srvr.dlock.release()
                    break

                elif self.data.startswith("6666SURVEYCOMPLETED"):
                    # add the player that has completed the survey
                    self.gui.players_completed_survey.append(self.player)
                    # get time of completion
                    tm = time.strftime(self.gui.timestamp_format)
                    # generate message for writing into results file
                    answers = self.data.split("@")[1] + ", " + tm
                    print("survey msg = ", answers)
                    self.gui.survey_answers[self.player.fakename] = answers
                    # msg = (tm + self.player.fakename +
                    #       "'s answers to the survey: " + survey_answers)

                    # if both player finished the survey, continue with
                    # instructions
                    if (len(self.gui.players_completed_survey) ==
                       len(self.gui.playerlist)):
                        #wx.CallAfter(self.gui.write_survey_to_results)
                        wx.CallAfter(self.gui.setup_instructions)

                # if all participants read the instructions, go on to
                # the buttons prototype
                elif (re.match(self.instructions_read_msg, self.data)):
                    self.gui.players_read_instructions.append(self.player)
                    if (len(self.gui.players_read_instructions) ==
                       len(self.gui.playerlist)):
                        wx.CallAfter(self.gui.on_new_round)

                elif (re.match(self.finished_buttons_msg, self.data)):
                    self.gui.players_finished_buttons.append(self.player)
                    if (len(self.gui.players_finished_buttons) ==
                       len(self.gui.playerlist)):
                        # all_readyToReadInstructions = all_ready
                        wx.CallAfter(self.gui.all_ready)

                elif (re.match(self.practice_msg, self.data)):
                    self.gui.players_ready.append(self.player)
                    if len(self.gui.players_ready) == len(self.gui.playerlist):
                        wx.CallAfter(self.gui.on_new_round)

                elif self.data.startswith("6666READYTOSTARTPROPERROUNDS"):
                    self.gui.player_count += 1
                    if self.gui.player_count == 1:
                        name = self.data.split("@")[1]
                        message = "9999ONLYONEPLAYERREADY9999"
                        encoded_message = self.gui.encode(message)
                        for player in self.gui.playerlist:
                            if player.realname == name:
                                player.clnt.send(encoded_message)
                    elif self.gui.player_count > 1:
                        self.gui.player_count = 0

                        # Decide on the open list of referents here?
                        wx.CallAfter(self.gui.on_new_round)

                elif (re.match(self.listener_msg, self.data)):
                    m = re.match(self.listener_msg, self.data)
                    # self.gui.listener_no = int(m.group(2))

                    self.gui.players_ready.append(self.player)
                    if len(self.gui.players_ready) == len(self.gui.playerlist):

                        self.gui.players_ready = []

                        wx.CallAfter(self.gui.on_new_round)

                elif (re.match(self.close_msg, self.data)):
                    self.gui.clients_closed.append(self.player)

                    if len(self.gui.clients_closed) == len(self.gui.playerlist):
                        wx.CallAfter(self.gui.final_results_read)

                elif re.match(self.info_msg, self.data):
                    # print("It's a match")
                    info_message = self.data
                    participant_name = info_message[8:-4]
                    self.player.realname = participant_name
                    self.gui.realnames[self.player.index] = participant_name
                    # So if we now have all the clients we want,
                    # we can start things off
                    if "?" not in self.gui.realnames:
                        establish_client_list()

                # Add elif here to send a server message to the client before the speaker draws.

                # Don't think we ever get in here~~
                elif re.match(self.pic_chosen_msg, self.data):
                    m = re.match(self.pic_chosen_msg, self.data)
                    # print("IN pic_chosen_msg DO NOT DELETE")

                    # get the important parts of the message, picture
                    # and speaker number
                    chosen_pic = m.group(1)
                    print("chosen = ", chosen_pic)
                    # self.gui.speaker_no = m.group(2)
                    # print("speaker name = ", self.gui.speaker_no)
                    # append the current player to the list
                    # (if the list is complete, the next round etc. can start)
                    self.gui.players_ready.append(self.player)
                    # create the message for the listener
                    # message = "9999PIC" + chosen_pic + "9999"
                    # encoded_message = self.gui.encode(message)
                    # for player in self.gui.playerlist:
                    #    player.clnt.send(encoded_message)


                # Server gets listener's guess and compares
                # it with the correct answer.
                # Also sends it to the speaker.
                elif re.match(self.listener_ref_chosen_msg, self.data):

                    m = re.match(self.listener_ref_chosen_msg, self.data)
                    # get the important parts of the message, picture
                    # and speaker number
                    currentGuess = m.group(1)
                    Glbl.currentGuess = currentGuess

                    referent = m.group(3)
                    Glbl.referent = referent

                    print("guessed referent = ", currentGuess)
                    # self.gui.listener_no = m.group(2)
                    # print("listener no = ", self.gui.listener_no)

                    # Updates the most recently logged value (list of lists) with whether the listener got it right
                    # print("referent before checkGuess()",referent)

                    if self.checkGuess(currentGuess=currentGuess,referent=referent):
                    #     update most recent entry in the dictionary with tuple. !!Check if this syntax is correct
                    #     - I want to manipulate in place !!
                    #     print("self.referent before getting from dict", self.referent)
                    #     print("full_message_dictionary before getting from dict", self.full_message_dictionary)
                    #     print("full_message_dictionary.get(referent) before getting from dict", self.full_message_dictionary.get(self.referent))


                        Glbl.full_message_dictionary[str(self.player.partner)][referent][-1]["correct"] = True
                        # print(Glbl.full_message_dictionary,"true")
                    else:

                        Glbl.full_message_dictionary[str(self.player.partner)][referent][-1]["correct"] = False
                        # print(Glbl.full_message_dictionary,"false")





                    # append the current player to the list
                    # (if the list is complete, the next round etc. can start)
                    self.gui.players_ready.append(self.player)
                    # create the message for the listener
                    message = "9999GUESS" + Glbl.currentGuess + "9999"

                    # send the message to the players
                    encoded_message = self.gui.encode(message)
                    for player in self.gui.playerlist:
                        player.clnt.send(encoded_message)

                # Sends speaker drawing to the listener

                # Pass the default dict too!!! -> they're going to be different
                # Maybe write a new class called metadata - sync server1 and server2
                elif re.match(self.coord_msg, self.data):

                    Glbl.substitution_round = False #Confirm/reestablish the default
                    
                    m = re.match(self.coord_msg, self.data)
                    # print("data from coord_msg", self.data)

                    filledStr = m.group(1)
                    print(filledStr,"filledStr")

                    # print("filled = ", filledStr)
                    filledArr = filledStr[1:-1]
                    print(filledArr,"filledArr")
                    filledArr = filledArr.split(", ")
                    filledArr = [int(i) for i in filledArr]

                    # self.gui.speaker_no = m.group(2)

                    # Add key:value (referent: coord vector) to the dictionary. Check if this tuple addition is correct
                    # Is tuple the right data structure?
                    # Append coords
                    Glbl.referent = m.group(3)
                    # Add referent to dictionary
                    Glbl.complexityTracker[Glbl.referent] = []

                    # print("correct referent - received from speaker", Glbl.referent)
                    single_message_dict = {}

                    single_message_dict["coords"]=filledArr
                    complexityScore = self.complexityScore(filledArr)
                    single_message_dict["complexity"]=complexityScore
                    single_message_dict["correct"] = None

                    # SOMETHING ISN'T BEING ADDED HERE??
                    # print("print full_message_dictionary before speaker update", Glbl.full_message_dictionary)
                    # print(Glbl.full_message_dictionary,"full_message_dictionary")
                    Glbl.full_message_dictionary[str(self.player)][Glbl.referent].append(single_message_dict)
                    # print("print full_message_dictionary after speaker update", Glbl.full_message_dictionary)




                    #Complexity substitution
                    # Complexity substitution paramaters - number of referents substituted, number of times substituted,
                    # minimum interval between substitutions

                    # TEST THIS
                    proportions = self.calculateProportion()
                    print("proportions before complexity", proportions)

                    # Used for TESTING complexitySubstitution
                    # testMode = True will always trigger the substitution
                    testMode = False #comment out when testing

                    # Uncomment when testing
                    # if Glbl.round > 0:
                    #     print("Tripped complexitySubstitutionTest")
                    #     testMode = True
                    #     filledArr = self.complexitySubstitution(filledArr, Glbl.complexityParam, testMode)
                    #     testMode = False
                    
                    param = Glbl.conditions[Glbl.condition_index]
                    if Glbl.referent in proportions[str(self.player)]:
                        prob = param[0][random.randint(0, 1)]
                        if proportions[Glbl.referent] >= prob:
                            Glbl.substitution_round=True
                            filledArr = self.complexitySubstitution(filledArr, testMode)





                        # if Glbl.experiment1 == True:
                        #     prob = Glbl.experiment1Param[0][random.randint(0, 1)]
                        #     if proportions[Glbl.referent] >= prob:
                        #         filledArr = self.complexitySubstitution(filledArr, testMode)
                        #         # print("SUBSTITUTED:", Glbl.referent)

                        # elif Glbl.experiment2 == True:
                        #     prob = Glbl.experiment2Param[0][random.randint(0, 1)]
                        #     if proportions[Glbl.referent] >= prob:
                        #         filledArr = self.complexitySubstitution(filledArr, testMode)

                        # elif Glbl.experiment3 == True:
                        #     prob = Glbl.experiment3Param[0][random.randint(0, 1)]
                        #     if proportions[Glbl.referent] >= prob:
                        #         filledArr = self.complexitySubstitution(filledArr, testMode)


                    # if Glbl.referent in proportions:
                    #     if proportions[Glbl.referent] >= self.sub_threshold:
                    #         filledArr = self.complexitySubstitution()



                    # print("speaker no = ", self.gui.speaker_no)
                    # append the current player to the list
                    # (if the list is complete, the next round etc. can start)
                    self.gui.players_ready.append(self.player)
                    # create the message for the listener

                    # Noise implementation
                    # TEST THIS

                    param = Glbl.conditions[Glbl.condition_index]
                    if param["noise"] != None and (Glbl.substitution_round == False or Glbl.substitution_noise_combine == True):
                        if random.random() <= param["noise"][0]: #does noise affect the signal at all?
                            filledArr = self.noise(filledArr)
                    #Need to ensure that both original and changed array are included in results



                    # if Glbl.experiment1 == True:
                    #     pass

                    # elif Glbl.experiment2 == True:
                    #     # experiment2Param = [(0.8, 0.8), (0.1, 0.3)]
                    #     prob = Glbl.experiment2Param[1][random.randint(0,1)]
                    #     filledArr = self.noise(filledArr, prob)

                    # elif Glbl.experiment3 == True:
                    #     prob = Glbl.experiment3Param[1][random.randint(0, 1)]
                    #     filledArr = self.noise(filledArr, prob)


                    Glbl.round += 1

                    # Convert filledArr to string and send to listener -
                    # print("filledStr before conversion of filledArr", filledStr)
                    filledStr = str(filledArr)
                    # filledStr = ", ".join(str(x) for x in filledArr)
                    # print("Check to see if filledArr is properly converted to filledStr", filledStr)

                    # Send coords and referent to the listener
                    message = "9999COORD" + filledStr + "@" + Glbl.referent + "9999"
                    print("server referent:", Glbl.referent)
                    # send the message to the listener
                    encoded_message = self.gui.encode(message)
                    for player in self.gui.playerlist:
                        player.clnt.send(encoded_message)

                elif re.match(self.qa_msg, self.data):
                    m = re.match(self.qa_msg, self.data)
                    qa = json.loads(m.group(1))
                    question = qa[0]
                    answer = qa[1]
                    qa4results = (self.player.realname +
                                  " (" + self.player.fakename +
                                  ") questionnaire answer:" +
                                  question + "\n" +
                                  answer + "\n\n")

                elif self.data == '/showserver' and self.gui.gui_show == 0:
                    wx.CallAfter(self.gui.on_reveal)
                else:
                    print("miscellaneous data: ", self.data)
                    pass

                Srvr.dlock.release()
            indata_list = []
        print("closing socket")
        self.myclntsock.close()


    # Methods I wrote
    # complexityScore and checkGuess are used for adding values to the tuple
    def complexityScore(self,coords):
        # Calculates the number of filled squares in a coord list

        score = sum(coords) #very simple! But best to keep this as a distinct function so that it can be adapted later if necessary.
        # score = 0
        # for i in coords:
        #     score = score + int(i)
        return score


    # Use this to update the full_message_dictionary tuple once the guess has been received from the listener
    def checkGuess(self,currentGuess,referent):
        # print(self.gui.playerlist,"playerlist")
        # print(self.gui.player_finder,"player_finder")
        # print(self.myclntsock,"myclntsock")
        # Check if the guess is correct.
        print(self.player,"self.player")
        if Glbl.referent == Glbl.currentGuess:
            return True
        else:
            return False
        # pass

    # dict_of_lists = [[coords], complexityscore, wasCorrect boolean]

    def calculateSingleProportion(self,message_list):
        correct = 0;

        if len(message_list) < 4:
            return -1
        for message_dict in message_list:
            if message_list["correct"] == True:
                correct = correct + 1
        return float(correct)/float(len(message_list))


    def calculateProportion(self):
        # dictionary noun:proportion
        proportions = {}
        for player in Glbl.full_message_dictionary:
            proportions[player] = {}
            for referent in Glbl.full_message_dictionary[player]:

                message_list = Glbl.full_message_dictionary[player][referent]
                current_proportion = self.calculateSingleProportion(message_list)
                if current_proportion != -1:
                    proportions[referent] = current_proportion
                # else:
                #     proportions[noun] = 0
            return proportions


    def getRefList(self):
        # Used to come up with a list of strings containing the open set of referents (8/12).
        # The target noun is the last one element.
        # Make sure that the correct referent is always an option. For any correct ref, include the set of possible
        # alternates.
        # Call this method and send the list of strings to both the speaker and the listener. The speaker needs to
        # display this in the speaker_draw_stage; listener needs to have these options (create in ListenerButtonsPanel)


        # Reset the sentRefList each round
        Glbl.sentRefList = []
        # Choose a random referent to display from totalRefList
        listLength = len(Glbl.totalRefList)
        refIndex = random.randint(0, listLength - 1)
        # print("Glbl sentRefList", Glbl.sentRefList)
        # print("length of Glbl sentRefList", len(Glbl.sentRefList))
        # Include the associated list - each ELEMENT!!
        if Glbl.totalRefList[refIndex] in Glbl.dogList:
            for element in Glbl.dogList:
                Glbl.sentRefList.append(element)
            # Glbl.sentRefList.extend(Glbl.dogList)
        elif Glbl.totalRefList[refIndex] in Glbl.foodList:
            for element in Glbl.foodList:
                Glbl.sentRefList.append(element)
            # Glbl.sentRefList.append(Glbl.foodList)
        elif Glbl.totalRefList[refIndex] in Glbl.plantList:
            for element in Glbl.plantList:
                Glbl.sentRefList.append(element)
            # Glbl.sentRefList.extend(Glbl.plantList)
        elif Glbl.totalRefList[refIndex] in Glbl.fruitList:
            for element in Glbl.fruitList:
                Glbl.sentRefList.append(element)
            # Glbl.sentRefList.extend(Glbl.fruitList)
        elif Glbl.totalRefList[refIndex] in Glbl.objectList:
            for element in Glbl.objectList:
                Glbl.sentRefList.append(element)
            # Glbl.sentRefList.extend(Glbl.objectList)

        # print("Glbl sentRefList after extending", Glbl.sentRefList)
        # print("length of Glbl sentRefList after extending", len(Glbl.sentRefList))

        shuffledTotalList = Glbl.totalRefList
        random.shuffle(shuffledTotalList)

        # Add the correct number of new referents (no duplicates) to the sentRefList
        i = 0
        while i < len(Glbl.totalRefList):
            # Check that there are no duplicates and sentRefList is smaller than the desired size.
            # If so, append the non-duplicate
            if shuffledTotalList[i] not in Glbl.sentRefList and len(Glbl.sentRefList) < 8:
                Glbl.sentRefList.append(shuffledTotalList[i])
            i = i + 1

        random.shuffle(Glbl.sentRefList)

        # print("Glbl sentRefList after adding fillers", Glbl.sentRefList)
        # Append the target noun to the back of the list -> WE CURRENTLY CHOOSE THE REFERENT IN THE CLIENT, line 1315
        # Glbl.sentRefList[-1] = Glbl.totalRefList[refIndex]
        # print("Glbl sentRefList after adding correct referent", Glbl.sentRefList)
        # print("Glbl sentRefList after adding correct referent", len(Glbl.sentRefList))

        return Glbl.sentRefList


    def mostComplex(self,referent):
        # Search through the tuple dictionary and find the most complex image
        targetList = Glbl.full_message_dictionary[referent]  #Is this done right?? -> target is a list of tuples
        mostComplex = 0
        mostComplexCoords = []

        # Find the most complex element in value: list of lists that was also matched correctly.
        for element in targetList:
            complexityScore = element[1]

            # THIS IS A BIG PROBLEM
            # FIX BY THINKING ABOUT HOW WE UPDATE THE CORRECT GUESS FIELD!!
            try:
                if complexityScore > mostComplex & (element[2] == True):
                    mostComplex = complexityScore
                    mostComplexCoords = element[0]

                # Used to deal with case where there is no correct match for a referent
            except IndexError:
                print("No correctly matched coords for given referent in full_message_dictionary")

        return mostComplexCoords
        # pass

    # Complexity tracker tracks the substituted referents, time from last use,
    def complexitySubstitution(self, filledArr, testMode):
        # Called when the flag is tripped & the referent matches complexity_referent
        # Call mostComplex to find the coord list with the most filled images.
        # Modify the message to send the mostComplex(referent) coords instead.

        # Complexity substitution parameters - number of referents substituted, max number of times substituted,
        # minimum interval between substitutions
        # complexityParam = [1, 1, 1]
        # Complexity tracker is a dictionary of lists
        # key : value
        # referent : (# subs, interval between last)
        # Substitutes the most complex referent if the referent has at minimum occurred complexityParam[0] times,
        # has been substitued less than complexityParam[1] times, and a minimum interval of complexityParam[2] has
        # occurred from the last substitution.

        if testMode == True:
            #     Testing
            print("SUBSTITUTED")
            return self.mostComplex(Glbl.referent)
        elif len(Glbl.complexityTracker.keys()) < Glbl.complexityParam["max_unique"] and \
                Glbl.complexityTracker[Glbl.referent][0] < Glbl.complexityParam["num_substitutions"] and \
                Glbl.complexityTracker[Glbl.referent][1] >= Glbl.complexityParam["min_interval"]:
            # Update complexityTracker
            Glbl.complexityTracker[Glbl.referent][0] += 1
            Glbl.complexityTracker[Glbl.referent][1] += 1
            print("SUBSTITUTED")
            return self.mostComplex(Glbl.referent)
        else:
            print("NOT SUBSTITUTED")
            return filledArr

        # subFilled = self.mostComplex(Glbl.referent) #Is this right??
        # return subFilled


    # Flips 1s to 0s if flag is above the threshold.
    def noise(filledArr):
        copy = filledArr
        for i in range(len(filledArr)):
            flag = random.random()
            if flag < noiseThreshold:
                copy[i] = 0
        return copy





    # def experiment1(threshold):

class ListenForClients(threading.Thread):
    """..."""

    def __init__(self, gui, host, port):
        """..."""
        threading.Thread.__init__(self)
        self.gui = gui
        # Symbolic name meaning all available interfaces
        self.host = host
        # Arbitrary non-privileged port
        self.port = port

    def run(self):
        """..."""
        try:
            ip_address = socket.gethostbyname(socket.gethostname())
            msg = 'Server IP: ' + str(ip_address)
            # HOST, PORT = "192.168.1.64", 9001
            # port between 1024 und 65535
        except socket.gaierror:
            msg = "Could not obtain Server IP. Obtain manually."

        wx.CallAfter(self.gui.screen_message, msg)
        wx.CallAfter(self.gui.screen_message, 'Waiting for clients...')
        for i in range(self.gui.nclnts):
            self.gui.realnames.append("?")
        while self.gui.finish == 0:
            lstn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # bins socket object to port & host
            lstn.bind((self.host, self.port))
            # Listen for clients (5 is maximum number to be queued.
            # System dependent, but usually 5)
            # We only need 2 or 4
            lstn.listen(4)
            # Wait for all clients to connect

            for i in range(self.gui.nclnts):
                (clnt, ap) = lstn.accept()
                s = Srvr(clnt, self.gui)
                newplayer = Player(clnt, self.gui, s)
                newplayer.index = i
                s.player = newplayer
                self.gui.playerlist.append(newplayer)
                tm = time.strftime(self.gui.timestamp_format)
                msg = tm + 'Client ' + str(i) + ' added'
                wx.CallAfter(self.gui.screen_message, msg)
                self.gui.threads.append(s)
                s.start()
                tm = time.strftime(self.gui.timestamp_format)
            msg = 'All clients connected'
            wx.CallAfter(self.gui.screen_message, msg)
            lstn.close()
            self.gui.allconnected = 1
            break


class Server:
    """..."""

    def __init__(self, parent, gui_show, nclnts, group_name, practice_path,
                 proper_path, images_path, results_path,
                 randomization, hard_mode, swapping, time_per_round, no_of_clicks):
        """..."""
        # The "False" parameter means "don't redirect stdout and stderr to a gui"
        app = wx.App(False)

        # instantiate the parameter file reader
        parameter_reader = Parameters(randomized=randomization)

        proper_rounds_config = parameter_reader.get_parameters_for_proper_rounds(proper_path)
        practice_rounds_config = parameter_reader.get_parameters_for_practice_rounds(practice_path)

        header = parameter_reader.header

        frame = Gui(parent, wx.ID_ANY, 'Server', gui_show, nclnts,
                    practice_rounds_config, proper_rounds_config, header,
                    group_name, images_path, results_path,
                    randomization, hard_mode, swapping, time_per_round, no_of_clicks)
        app.MainLoop()
