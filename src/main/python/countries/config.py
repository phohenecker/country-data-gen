# -*- coding: utf-8 -*-


import os
import random
import typing

import insanity

from argmagic import decorators

from countries import problem_setting


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


class Config(object):
    """This class contains all of the user-defined configuration for running the data generator."""
    
    DEFAULT_CLASS_FACTS = False
    """bool: Default value of attribute :attr:`class_facts`."""
    
    DEFAULT_MINIMAL = False
    """bool: Default value of attribute :attr:`minimal`."""
    
    DEFAULT_NUM_DATASETS = 1
    """int: Default value of attribute :attr:`num_datasets`."""
    
    DEFAULT_NUM_TRAINING_SAMPLES = 5000
    """int: Default value of attribute :attr:`num_training_samples`."""
    
    DEFAULT_OUTPUT_DIR = "./out"
    """str: Default value of attribute :attr:`output_dir`."""
    
    DEFAULT_QUIET = False
    """bool: Default value of attribute :attr:`quiet`."""
    
    DEFAULT_SETTING = problem_setting.ProblemSetting.S1.value
    """str: Default value of attribute :attr:`setting`."""
    
    #  CONSTRUCTOR  ####################################################################################################
    
    def __init__(self):
        """Creates a new instance of ``Config`` that describes the default configuration."""
        # for a description of the following attributes, confer the respective properties
        self._class_facts = self.DEFAULT_CLASS_FACTS
        self._data = None
        self._dlv = None
        self._minimal = self.DEFAULT_MINIMAL
        self._num_datasets = self.DEFAULT_NUM_DATASETS
        self._num_training_samples = self.DEFAULT_NUM_TRAINING_SAMPLES
        self._output_dir = self.DEFAULT_OUTPUT_DIR
        self._quiet = self.DEFAULT_QUIET
        self._seed = random.randrange(100000)
        self._setting = self.DEFAULT_SETTING

    #  PROPERTIES  #####################################################################################################
    
    @property
    def class_facts(self) -> bool:
        """bool: Specifies whether to include classes as facts."""
        return self._class_facts
    
    @class_facts.setter
    def class_facts(self, class_facts: bool) -> None:
        self._class_facts = bool(class_facts)
        
    @decorators.optional
    @property
    def data(self) -> typing.Optional[str]:
        """str: The path of the JSON file that contains the data. If not provided, then the data is downloaded instead.
        """
        return self._data
    
    @data.setter
    def data(self, data: str) -> None:
        data = str(data)
        if not os.path.isfile(data):
            raise ValueError("The provided <data> does not refer to an existing file: '{}'!".format(data))
        self._data = data
    
    @property
    def dlv(self) -> typing.Optional[str]:
        """str: The path to the DLV executable to use."""
        return self._dlv
    
    @dlv.setter
    def dlv(self, dlv: str) -> None:
        dlv = str(dlv)
        if not os.path.isfile(dlv):
            raise ValueError("<dlv> does not refer to an existing file: '{}'!".format(dlv))
        self._dlv = dlv
    
    @property
    def num_datasets(self) -> int:
        """int: The total number of datasets to generate."""
        return self._num_datasets
    
    @num_datasets.setter
    def num_datasets(self, num_datasets: int) -> None:
        insanity.sanitize_type("num_datasets", num_datasets, int)
        insanity.sanitize_range("num_samples", num_datasets, minimum=1)
        self._num_datasets = num_datasets

    @property
    def num_training_samples(self) -> int:
        """int: The total number of training samples to generate for each dataset."""
        return self._num_training_samples

    @num_training_samples.setter
    def num_training_samples(self, num_training_samples: int) -> None:
        insanity.sanitize_type("num_training_samples", num_training_samples, int)
        insanity.sanitize_range("num_training_samples", num_training_samples, minimum=1)
        self._num_training_samples = num_training_samples
    
    @property
    def output_dir(self) -> str:
        """str: The path of the directory that the generated data is placed in."""
        return self._output_dir
    
    @output_dir.setter
    def output_dir(self, output_dir: str) -> None:
        self._output_dir = str(output_dir)
    
    @property
    def quiet(self) -> bool:
        """bool: Tells the application to be quiet."""
        return self._quiet
    
    @quiet.setter
    def quiet(self, quiet: bool) -> None:
        self._quiet = bool(quiet)
    
    @decorators.optional
    @property
    def seed(self) -> typing.Optional[int]:
        """int: The seed to use for initializing the RNG."""
        return self._seed
    
    @seed.setter
    def seed(self, seed: int) -> None:
        insanity.sanitize_type("seed", seed, int)
        self._seed = seed
    
    @decorators.exhaustive(problem_setting.ProblemSetting)
    @property
    def setting(self) -> str:
        """str: The considered problem setting, which has to one of S1, S2, and S3."""
        return self._setting
    
    @setting.setter
    def setting(self, setting: str) -> None:
        setting = str(setting)
        insanity.sanitize_value("setting", setting, [s.value for s in problem_setting.ProblemSetting])
        self._setting = setting
