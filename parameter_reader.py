#!/usr/bin/python2
# -*- coding: utf-8 -*-
# title           :configuration.py
# description     :collects the configuration from the config.csv file
# author          :Lisa Raithel and Jon Stevens, ZAS, Berlin
# usage           :python configuration.py
# notes           :-
# python_version  :2.7.6

import codecs
import collections
import csv
import sys
import random

class Parameters:
    """Represents the configuration information read
    from a csv file.

    """
    def __init__(self,randomized):
        """Initialises the configuration class

        """
        self.header = []
        self.randomized = randomized

    def get_parameters_for_proper_rounds(self, config_file):
        """Read all information given in the configuration file and
        collects the information in a default dict.
        """
        delim = self._get_delimiter(config_file)
        with codecs.open(config_file, "r", "utf-8") as read_handle:
            reader = csv.reader(read_handle, delimiter=delim)
            counter = 0
            cf_info = collections.defaultdict(lambda: collections.defaultdict(str))
            for line in reader:
                if counter > 0:
                    if line != []:
                        # collect all information that is given in
                        # a default dict:
                        round_no = int(line[0].strip())
                        image_1 = line[1].strip()
                        image_2 = line[2].strip()
                        config = collections.defaultdict(str)
                        config[u"image_1"] = image_1
                        config[u"image_2"] = image_2
                        cf_info[round_no] = config
                else:
                    self.header.append("Trial")
                    for element in line:
                        self.header.append(element.encode("utf8"))

                    print("header = ", self.header)
                counter += 1

        if self.randomized:
            cf_info = dict(zip(random.sample(cf_info.keys(),len(cf_info.keys())),cf_info.values()))

        print("cf info = ", cf_info)
        return(cf_info)

    def get_parameters_for_practice_rounds(self, config_file):
        """Read all information given in the configuration file and
        collects the information in a default dict.
        """
        delim = self._get_delimiter(config_file)
        with codecs.open(config_file, "r", "utf-8") as read_handle:
            reader = csv.reader(read_handle, delimiter=delim)
            counter = 0
            practice_rounds_config = collections.defaultdict(lambda: collections.defaultdict(str))
            for line in reader:
                if counter > 0:
                    if line != []:
                        round_no = int(line[0].strip())
                        image_1 = line[1].strip()
                        image_2 = line[2].strip()
                        config = collections.defaultdict(str)
                        config[u"image_1"] = image_1
                        config[u"image_2"] = image_2

                        practice_rounds_config[round_no] = config

                counter += 1

        return(practice_rounds_config)

    def _get_delimiter(self, csv_file):
        with codecs.open(csv_file, "r", "utf-8") as read_handle:
            header = read_handle.readline()
            print("header = ", header)
            if header.find(";") != -1:
                return(";")
            elif header.find(",") != -1:
                return(",")
            #elif header.find("\s") != -1:
            #    return("\t")
            else:
                # set dedault to ";"
                return(";")




if __name__ == "__main__":
    test_file = sys.argv[1]
    cf = Parameters(test_file)
    config = cf.get_parameters()
