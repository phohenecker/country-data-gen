# -*- coding: utf-8 -*-


import os
import random
import typing

import insanity

from argmagic import decorators

from countries import problem_setting


__author__ = "Patrick Hohenecker"
__copyright__ = (
        "Copyright (c) 2018 Patrick Hohenecker\n"
        "\n"
        "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
        "of this software and associated documentation files (the \"Software\"), to deal\n"
        "in the Software without restriction, including without limitation the rights\n"
        "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
        "copies of the Software, and to permit persons to whom the Software is\n"
        "furnished to do so, subject to the following conditions:\n"
        "\n"
        "The above copyright notice and this permission notice shall be included in all\n"
        "copies or substantial portions of the Software.\n"
        "\n"
        "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
        "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
        "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
        "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
        "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
        "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
        "SOFTWARE."
)
__license__ = "MIT License"
__version__ = "2018.1"
__date__ = "Mär 15, 2018"
__maintainer__ = "Patrick Hohenecker"
__email__ = "mail@paho.at"
__status__ = "Development"


class Config(object):
    """This class contains all of the user-defined configuration for running the data generator."""
    
    DEFAULT_CLASS_FACTS = False
    """bool: Default value of attribute :attr:`class_facts`."""
    
    DEFAULT_DLV = "src/main/resources/dlv.i386-apple-darwin.bin"
    """str: Default value of attribute :attr:`dlv`."""
    
    DEFAULT_MINIMAL = False
    """bool: Default value of attribute :attr:`minimal`."""
    
    DEFAULT_NUM_DATASETS = 1
    """int: Default value of attribute :attr:`num_datasets`."""
    
    DEFAULT_NUM_TRAINING_SAMPLES = 100
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
        self._dlv = self.DEFAULT_DLV
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
    def minimal(self) -> bool:
        """bool: Specifies whether to confine inferences to locatedIn predicates from the target set."""
        return self._minimal
    
    @minimal.setter
    def minimal(self, minimal: bool) -> None:
        self._minimal = bool(minimal)
    
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
