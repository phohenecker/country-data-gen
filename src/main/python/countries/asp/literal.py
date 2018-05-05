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
import re
import typing

import insanity


class Literal(object):
    """Instances of this class represent single literals."""
    
    PREDICATE_PATTERN = "^[a-z][a-zA-Z0-9]*$"
    """str: A regular expression that describes legal predicate symbols."""
    
    TERM_PATTERN = PREDICATE_PATTERN
    """str: A regular expression that describes legal terms."""
    
    #  CONSTRUCTORS  ###################################################################################################
    
    def __init__(self, predicate: str, terms: typing.Iterable[str]=None, positive: bool=True):
        """Creates a new instance of ``Literal``.
        
        An example of a positive literal is ``country(austria)``, and a negative one is ``~locatedIn(germany, africa)``.
        The predicates that appear in these literals are ``country`` and ``locatedIn``, respectively, and the terms are
        ``austria`` in the former example and both ``germany`` and ``africa`` in the latter.
        
        Args:
            predicate (str): The predicate symbol that appears in the literal. A predicate symbol has to be
                alphanumeric, starting with a lower-case letter.
            terms (iterable[str], optional): The terms that appear in the literal in the order that they can be iterated
                over. Each term has to be an alphanumeric string starting with a lower-case letter.
            positive (bool, optional): Indicates whether the literal is positive or negative, i.e., an atom or a negated
                atom. By default, this parameters is ``True``.
        
        Raises:
            TypeError: If ``terms``, given that it has been provided, is not iterable.
            ValueError: If ``predicate`` does not specify a legal predicate symbol or if any of the provided terms is
                not a legal one.
        """
        # sanitize args
        predicate = str(predicate)
        if len(predicate) == 0:
            raise ValueError("The parameter <predicate> must not be the empty string!")
        if not re.match(self.PREDICATE_PATTERN, predicate):
            raise ValueError("The provided <predicate> is not a legal predicate symbol: '{}'!".format(predicate))
        if terms is not None:
            insanity.sanitize_type("terms", terms, collections.Iterable)
            terms = tuple(str(t) for t in terms)
            for t in terms:
                if len(t) == 0:
                    raise ValueError("None of the terms can be the empty string!")
                if not re.match(self.TERM_PATTERN, t):
                    raise ValueError(
                        "The provided <terms> contain an illegal expression: '{}'!".format(t))
        positive = bool(positive)
        
        # define attributes
        self._positive = positive
        self._predicate = predicate
        self._terms = terms
    
    #  MAGIC FUNCTIONS  ################################################################################################
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Literal) and str(other) == str(self)
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __str__(self) -> str:
        return "{}{}({})".format(
                "" if self._positive else "~",
                self._predicate,
                ",".join(self._terms)
        )
    
    #  PROPERTIES  #####################################################################################################
    
    @property
    def positive(self) -> bool:
        """bool: Indicates whether the literal is a positive one."""
        return self._positive
    
    @property
    def predicate(self) -> str:
        """str: The predicate symbol that appears in the literal."""
        return self._predicate
    
    @property
    def terms(self) -> typing.Optional[typing.Tuple[str]]:
        """tuple: The terms that appear in the literal or ``None`` if it is of arity 0."""
        return self._terms
