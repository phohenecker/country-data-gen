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
import itertools
import typing

import insanity

from countries.asp import literal


class AnswerSet(object):
    """Instances of this class represent single answer sets."""
    
    def __init__(self, facts: typing.Iterable[literal.Literal], inferences: typing.Iterable[literal.Literal]):
        """Creates a new instance of ``AnswerSet``.
        
        Args:
            facts (list[:class:`literal.Literal`]): The facts contained in the answer set.
            inferences (list[:class:`literal.Literal`]): The inferences contained in the answer set.
        
        Raises:
            TypeError: If any of ``facts`` and ``inferences`` is not an ``Iterable`` of instances of type
                :class:`literal.Literal`.
        """
        # sanitize args
        insanity.sanitize_type("facts", facts, collections.Iterable)
        facts = list(facts)
        insanity.sanitize_iterable("facts", facts, elements_type=literal.Literal)
        insanity.sanitize_type("inferences", inferences, collections.Iterable)
        inferences = list(inferences)
        insanity.sanitize_iterable("inferences", inferences, elements_type=literal.Literal)
        
        # define attributes
        self._facts = facts
        self._inferences = inferences
    
    #  MAGIC FUNCTIONS  ################################################################################################
    
    def __iter__(self) -> typing.Iterator[literal.Literal]:
        return itertools.chain(self._facts, self._inferences)
        
    #  PROPERTIES  #####################################################################################################
    
    @property
    def facts(self) -> typing.List[literal.Literal]:
        """list[:class:`literal.Literal`]: The facts contained in the answer set."""
        return self._facts[:]
    
    @property
    def inferences(self) -> typing.List[literal.Literal]:
        """list[:class:`literal.Literal`]: The inferences contained in the answer set."""
        return self._inferences[:]
