# -*- coding: utf-8 -*-


import typing


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
__date__ = "Mar 16, 2018"
__maintainer__ = "Patrick Hohenecker"
__email__ = "mail@paho.at"
__status__ = "Development"


class Country(object):
    """Instances of this class encapsulate all of the relevant information about a single country.
    
    Attributes:
        name (str): The country's name.
        neighbors (list[str]): The names of all neighboring countries as list.
        subregion (str): The name of the subregion that the country belongs to.
        region (str): The name of the region that the country belongs to.
    """
    
    def __init__(self, name: str, neighbors: typing.List[str], region: str, subregion: str):
        """Creates a new instance of ``Country`` that stores the provided data (literally).
        
        Args:
            name (str): See :attr:`name`.
            neighbors (list[str]): See :attr:`neighbors`.
            region (str): See :attr:`region`.
            subregion (str): See :attr:`subregion`.
        """
        
        self.name = name
        self.neighbors = neighbors
        self.region = region
        self.subregion = subregion
