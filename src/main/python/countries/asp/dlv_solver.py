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


import collections
import os
import re
import subprocess
import typing

import insanity

from countries.asp import answer_set
from countries.asp import base_solver
from countries.asp import literal


class DlvSolver(base_solver.BaseSolver):
    """A wrapper class for the DLV system."""
    
    LITERAL_PATTERN = r"^(?P<sign>[-~]?)(?P<predicate>.+)\((?P<terms>.+)\)$"
    """str: A regular expression for parsing literals provided by DLV."""
    
    #  CONSTRUCTOR  ####################################################################################################
    
    def __init__(self, exe_path: str):
        """Creates a new instance of ``DlvSystem``.
        
        Args:
            exe_path (str): See :meth:`base_solver.BaseSolver.__init__`.
        """
        super().__init__(exe_path)
    
    #  METHODS  ########################################################################################################
    
    def run(self, path: str, facts: typing.List[literal.Literal]) -> answer_set.AnswerSet:
        # sanitize args
        path = str(path)
        if not os.path.isfile(path):
            raise ValueError("The provided <path> does not refer to an existing file: '{}'!".format(path))
        insanity.sanitize_type("facts", facts, collections.Iterable)
        facts = set(facts)
        insanity.sanitize_iterable("facts", facts, elements_type=literal.Literal)
        
        # prepare facts as single string to provide to DLV
        str_facts = ". ".join(str(f) for f in facts)
        if str_facts:
            str_facts += "."
        
        # run DLV
        cmd = "echo \"{}\" | {} -silent -- {}".format(
                str_facts,
                self._exe_path,
                path
        )
        result = str(subprocess.check_output(cmd, shell=True, universal_newlines=True)).strip()
        
        # collect inferences
        inferences = set()
        for x in result[1:-1].split(", "):
            m = re.match(self.LITERAL_PATTERN, x)
            lit = literal.Literal(
                    m.group("predicate"),
                    m.group("terms").split(","),
                    positive=m.group("sign") == ""
            )
            if lit not in facts:
                inferences.add(lit)
        
        return answer_set.AnswerSet(facts, inferences)
