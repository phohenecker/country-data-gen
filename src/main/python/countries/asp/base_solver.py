# -*- coding: utf-8 -*-


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
__license__ = "Simplified BSD License"
__version__ = "2018.1"
__date__ = "May 04, 2018"
__maintainer__ = "Patrick Hohenecker"
__email__ = "mail@paho.at"
__status__ = "Development"


import abc
import os
import typing

from countries.asp import answer_set
from countries.asp import literal


class BaseSolver(metaclass=abc.ABCMeta):
    """An abstract base class for wrappers that provide access to ASP solvers."""
    
    def __init__(self, exe_path: str):
        """Creates a new instance of ``BaseSolver``.
        
        Args:
            exe_path (str): The path to an executable for running the wrapped solver.
        """
        if not os.path.isfile(exe_path):
            raise ValueError("The provided <exe_path> does not refer to an existing file: '{}'!".format(exe_path))
        
        self._exe_path = str(exe_path)
        
    #  PROPERTIES  #####################################################################################################
    
    @property
    def exe_path(self) -> str:
        """str: The path to the executable that is used to run the wrapped ASP solver."""
        return self._exe_path
    
    #  METHODS  ########################################################################################################
    
    @abc.abstractmethod
    def run(self, path, facts: typing.Iterable[literal.Literal]) -> answer_set.AnswerSet:
        """Runs the ASP program at the provided path, and provides the created answer set.
        
        Args:
            path (str): The path of the ASP program to run.
            facts (iterable[:class:`literal.Literal`]): The facts to provide to the solver in addition to the ASP
                program.
        
        Returns:
            :class:`answer_set.AnswerSet`: The created answer set.
        
        Raises:
            CalledProcessError: If the invoked ASP solver raises any error.
            TypeError: If ``facts`` is not an ``Iterable`` of instances of type :class:`literal.Literal`.
            ValueError: If ``path`` does not refer to an existing path.
        """
