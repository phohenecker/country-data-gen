#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Runs the generator with the configuration specified by the command line args."""


import collections
import json
import os
import random
import sys
import typing
import urllib.request

import argmagic
import streamtologger

from aspwrapper import dlv_solver

from countries import config
from countries import country
from countries import dataset_generator as data_gen


__author__ = "Patrick Hohenecker"
__copyright__ = (
        "Copyright (c) 2018, Patrick Hohenecker\n"
        "All rights reserved.\n"
        "\n"
        "Redistribution and use in source and binary forms, with or without\n"
        "modification, are permitted provided that the following conditions are met:\n"
        "\n"
        "1. Redistributions of source code must retain the above copyright notice, this\n"
        "   list of conditions and the following disclaimer.\n"
        "2. Redistributions in binary form must reproduce the above copyright notice,\n"
        "   this list of conditions and the following disclaimer in the documentation\n"
        "   and/or other materials provided with the distribution.\n"
        "\n"
        "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" AND\n"
        "ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED\n"
        "WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE\n"
        "DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR\n"
        "ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES\n"
        "(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;\n"
        "LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND\n"
        "ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT\n"
        "(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS\n"
        "SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
)
__license__ = "BSD-2-Clause"
__version__ = "2018.1"
__date__ = "Mar 15, 2018"
__maintainer__ = "Patrick Hohenecker"
__email__ = "mail@paho.at"
__status__ = "Development"


APP_DESCRIPTION = (
        "This is a tool for generating datasets of reasoning tasks about countries and regions. "
        "For additional details, have a look at the project repository at "
        "https://github.com/phohenecker/country-data-gen."
)
"""str: The help text that is printed for this app if --help is provided."""

APP_NAME = "run-data-gen.sh"
"""str: The name that is displayed in the synopsis of this app."""

DATA_FILENAME = "countries.json"
"""str: The filename that is used for storing the data."""

DATA_URL = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
"""str: The URL for downloading the data, which is specified in JSON format."""

LOG_FILE_NAME = "out.log"
"""str: The filename of the created log file."""

ONTOLOGY = "src/main/asp/ontology.asp"
"""str: The path to the ASP program that describes the used ontology."""


ISO_CODE_KEY = "cca3"
"""str: The key that is used to store the ISO 3166-1 alpha-3 code for countries, e.g., 'AUT', in the data file."""

NEIGHBORS_KEY = "borders"
"""str: The key that is used to store a country's neighbors in the data file."""

REGION_KEY = "region"
"""str: The key that is used to store a country's region in the data file."""

SUBREGION_KEY = "subregion"
"""str: The key that is used to store a country's subregion in the data file."""


def _load_data(path: str) -> typing.Dict[str, country.Country]:
    """Loads the raw data from the provided path.

    The path is supposed to point to a JSON file that specifies countries and regions in the format that is used in
    the original `GitHub repository <https://github.com/mledoze/countries>`_.

    Args:
        path (str): The path to the JSON file that contains the data.
    """
    
    # read the provided file
    with open(path, "r") as f:
        data = json.load(f)
    
    # create mapping from ISO codes to actual (readable) names
    names = {c[ISO_CODE_KEY]: c["name"]["official"] for c in data}
    
    # assemble a dictionary that maps from (ISO code) names to instances of country.Country
    return collections.OrderedDict(
            (
                    (
                            names[c[ISO_CODE_KEY]],
                            country.Country(
                                    c[ISO_CODE_KEY],
                                    [names[n] for n in c[NEIGHBORS_KEY]],
                                    c[REGION_KEY],
                                    None if not c[SUBREGION_KEY] else c[SUBREGION_KEY]
                            )
                    )
                    for c in data
            )
    )


def _print_config(conf: config.Config) -> None:
    """Prints the provided configuration as table to the screen.
    
    Args:
        conf (:class:`config.Config`): The configuration to print.
    """
    # parse and sort the config into (name, value) pairs
    str_conf = sorted(argmagic.get_config(conf).items(), key=lambda x: x[0])
    
    # compute the maximum (string) lengths of all names and values, respectively
    max_name_len = max((len(n) for n, _ in str_conf))
    max_value_len = max((len(v) for _, v in str_conf))
    
    # assemble a horizontal separator
    h_line = "=" * (max_name_len + max_value_len + 3)
    
    # print the config to the screen
    print(h_line)
    print("CONFIGURATION")
    print(h_line)
    for name, value in str_conf:
        print(("{:" + str(max_name_len) + "} : {}").format(name, value))
    print(h_line)
    print()


def main(conf: config.Config):
    
    # create the output directory if it does not exist yet
    if not os.path.isdir(conf.output_dir):
        os.mkdir(conf.output_dir)

    # set up logging
    streamtologger.redirect(
            target=os.path.join(conf.output_dir, LOG_FILE_NAME),
            print_to_screen=not conf.quiet,
            header_format="[{timestamp:%Y-%m-%d %H:%M:%S} - {level:5}]  ",
            append=False
    )

    # print command that was used to run this application
    print("$", APP_NAME, " ".join(sys.argv[1:]))
    print()
    
    # print the provided configuration
    _print_config(conf)
    
    # seed RNG if possible
    if conf.seed is not None:
        print("seeding RNG with {}".format(conf.seed))
        random.seed(conf.seed)
        print("OK\n")
    
    # look for data, and download it if necessary
    print("looking for data...")
    if conf.data is None:
        data_path = os.path.join(conf.output_dir, DATA_FILENAME)
        if os.path.isfile(data_path):
            print("discovered data at '{}'".format(data_path))
        else:
            print("downloading data to '{}'...".format(data_path))
            urllib.request.urlretrieve(DATA_URL, data_path)
        conf.data = data_path
        print("OK\n")
    
    # load the data from disk
    print("loading data from '{}'...".format(conf.data))
    data = _load_data(conf.data)
    print("found data about {} countries".format(len(data)))
    print("OK\n")
    
    # invoke dataset generator to create the required datasets
    print(
            "generating {} dataset{} with {} training sample{}\n".format(
                    conf.num_datasets,
                    "s" if conf.num_datasets > 1 else "",
                    conf.num_training_samples,
                    "s" if conf.num_training_samples > 1 else ""
            )
    )
    generator = data_gen.DatasetGenerator(
            data,
            conf.setting,
            dlv_solver.DlvSolver(conf.dlv),
            ONTOLOGY,
            conf.class_facts
    )
    generator.generate_datasets(conf.num_datasets, conf.num_training_samples, conf.output_dir)
    

main(argmagic.parse_args(config.Config, app_name=APP_NAME, app_description=APP_DESCRIPTION))
