# -*- coding: utf-8 -*-


import typing

from reldata.data import knowledge_graph as kg


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
__date__ = "Mar 17, 2018"
__maintainer__ = "Patrick Hohenecker"
__email__ = "mail@paho.at"
__status__ = "Development"


class Dataset(object):
    """Instances of this class represent training datasets.
    
    Any training datasets consists of knowledge graphs for training, evaluation (dev), and testing.
    
    Attributes:
        dev (kg.KnowledgeGraph): The knowledge graph for evaluation.
        test (kg.KnowledgeGraph): The knowledge graph for testing.
        train (list[kg.KnowledgeGraph]): A list of knowledge graphs for training.
    """
    
    def __init__(self, train: typing.List[kg.KnowledgeGraph], dev: kg.KnowledgeGraph, test: kg.KnowledgeGraph):
        """Creates a new instance of ``Dataset`` that stores the provided split (literally).
        
        Args:
            train (list[kg.KnowledgeGraph]): See :attr:`train`.
            dev (kg.KnowledgeGraph): See :attr:`dev`.
            test (kg.KnowledgeGraph): See :attr:`test`.
        """
        self.dev = dev
        self.test = test
        self.train = train
