# -*- coding: utf-8 -*-


import collections
import itertools
import json
import typing
import unittest

from reldata.data import individual as ind
from reldata.data import knowledge_graph as kg

from countries import country
from countries import dataset_generator as dg
from countries import problem_setting as ps
from countries import vocabulary as voc


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
__date__ = "Mar 17, 2018"
__maintainer__ = "Patrick Hohenecker"
__email__ = "mail@paho.at"
__status__ = "Development"


class DatasetGeneratorTest(unittest.TestCase):
    
    ISO_CODE_KEY = "cca3"
    """str: The key that is used to store the ISO 3166-1 alpha-3 code for countries, e.g., 'AUT', in data files."""
    
    NEIGHBORS_KEY = "borders"
    """str: The key that is used to store a country's neighbors in data files."""
    
    REGION_KEY = "region"
    """str: The key that is used to store a country's region in data files."""
    
    SUBREGION_KEY = "subregion"
    """str: The key that is used to store a country's subregion in data files."""
    
    TEST_DATA_PATH = "src/test/resources/countries.json"
    """str: The path to the JSON file that contains the test data."""
    
    #  METHODS  ########################################################################################################
    
    def _check_s1(self, sample: kg.KnowledgeGraph) -> None:
        """Checks whether the provided samples obeys the rules of problem variant S1."""
        countries, has_region, has_subregion = self._classify_countries(sample)

        # CHECK: every country has a subregion
        self.assertEqual(set(countries.keys()), has_subregion)
        
        # CHECK: the number of countries that do not have a region specified equals NUM_EVAL_COUNTRIES
        self.assertEqual(dg.DatasetGenerator.NUM_EVAL_COUNTRIES, len(has_subregion - has_region))

    def _check_s2(self, sample: kg.KnowledgeGraph) -> None:
        """Checks whether the provided samples obeys the rules of problem variant S2."""
        countries, has_region, has_subregion = self._classify_countries(sample)
    
        # CHECK: every country has either both a region and a subregion or neither of them
        self.assertEqual(has_region, has_subregion)

        # CHECK: the number of countries that do not have a region specified equals NUM_EVAL_COUNTRIES
        self.assertEqual(dg.DatasetGenerator.NUM_EVAL_COUNTRIES, len(countries) - len(has_region))

    def _check_s3(self, sample: kg.KnowledgeGraph) -> None:
        """Checks whether the provided samples obeys the rules of problem variant S3."""
        countries, has_region, has_subregion = self._classify_countries(sample)
        all_countries = set(countries.keys())

        # fetch target countries and their neighbors
        target_countries = all_countries - has_subregion
        target_neighbors = set()
        for c in target_countries:
            target_neighbors |= {n for n in countries[c] if n not in target_countries}

        # CHECK: the number of target countries, i.e., those that do not have a subregion specified,
        #        equals NUM_EVAL_COUNTRIES
        self.assertEqual(dg.DatasetGenerator.NUM_EVAL_COUNTRIES, len(target_countries))
        
        # CHECK: the target countries, i.e., those without subregion, do not have a region specified either
        for c in target_countries:
            self.assertNotIn(c, has_region)
        
        # iterate over all neighbors of target countries
        for n in target_neighbors:

            # CHECK: every neighbor of a target country has a subregion
            self.assertIn(n, has_subregion)
            
            # CHECK: no neighbor of a target country  has a region
            self.assertNotIn(n, has_region)
        
        # CHECK: all countries that are neither targets nor neighbors of such have both a region and a subregion
        for c in all_countries - target_countries - target_neighbors:
            self.assertIn(c, has_region)
            self.assertIn(c, has_subregion)
    
    @staticmethod
    def _classify_countries(
            sample: kg.KnowledgeGraph
    ) -> typing.Tuple[
            typing.Dict[ind.Individual, typing.Set[ind.Individual]],
            typing.Set[ind.Individual],
            typing.Set[ind.Individual]
    ]:
        """Analyzes the countries that are contained in the provided knowledge graph.
        
        Args:
            sample (kg.KnowledgeGraph): The sample whose countries are being analyzed.
            
        Returns:
            tuple: A ``dict`` mapping countries to sets of their neighbors, a set of all countries that are prediction
                targets, and all countries that are neighbors of prediction targets but not targets by themselves.
                Notice that countries are represented as instances of ``ind.Individual`` rather than strings.
        """
        # fetch all countries from the provided samples
        countries = {}  # maps countries to sets of their neighbors
        regions = set()
        subregions = set()
        
        # extract all countries and regions/subregions from the sample
        for i in sample.individuals:
            for cls_mem in i.classes:
                if cls_mem.cls.name == voc.CLASS_COUNTRY:
                    if cls_mem.is_member:
                        countries[i] = set()
                elif cls_mem.cls.name == voc.CLASS_REGION:
                    if cls_mem.is_member:
                        regions.add(i)
                elif cls_mem.cls.name == voc.CLASS_SUBREGION:
                    if cls_mem.is_member:
                        subregions.add(i)

        has_region = set()
        has_subregion = set()
        
        for triple in sample.triples:
    
            s, p, o = triple
            
            if triple.inferred or not triple.positive or s not in countries:
                continue
            
            if p.name == voc.RELATION_LOCATED_IN:
                if o in regions:
                    has_region.add(s)
                elif o in subregions:
                    has_subregion.add(s)
                else:
                    raise ValueError("Encountered expected object located-in triple: ''!".format(o.name))
            elif p.name == voc.RELATION_NEIGHBOR_OF:
                countries[s].add(o)
            else:
                raise ValueError("Encountered unknown relation: ''!".format(p.name))

        return countries, has_region, has_subregion

    def setUp(self):
        # read the test data
        with open(self.TEST_DATA_PATH, "r") as f:
            data = json.load(f)
    
        # assemble a dictionary that maps from (ISO code) names to country objects
        self.data = collections.OrderedDict(
                (
                        (
                                c[self.ISO_CODE_KEY],
                                country.Country(
                                        c[self.ISO_CODE_KEY],
                                        c[self.NEIGHBORS_KEY],
                                        c[self.REGION_KEY],
                                        "no-subregion" if not c[self.SUBREGION_KEY] else c[self.SUBREGION_KEY]
                                )
                        )
                        for c in data
                )
        )
    
    def test_generate_sample(self):
        # generate samples for all three scenarios
        s1_sample = dg.DatasetGenerator(self.data, ps.ProblemSetting.S1.value)._generate_sample(list(self.data.keys()))
        s2_sample = dg.DatasetGenerator(self.data, ps.ProblemSetting.S2.value)._generate_sample(list(self.data.keys()))
        s3_sample = dg.DatasetGenerator(self.data, ps.ProblemSetting.S3.value)._generate_sample(list(self.data.keys()))
        
        # CHECK: the generated sample obeys the rules of the according problem settings
        self._check_s1(s1_sample)
        self._check_s2(s2_sample)
        self._check_s3(s3_sample)
    
    def test_split_countries(self):
        # since _split_countries involves randomness, we perform the tests multiple times
        for _ in range(20):
            
            # create a train/dev/test split
            data_gen = dg.DatasetGenerator(self.data, ps.ProblemSetting.S1.value)
            train, dev, test = data_gen._split_countries()

            # CHECK: the retrieved lists are of the correct length
            self.assertEqual(dg.DatasetGenerator.NUM_EVAL_COUNTRIES, len(dev))
            self.assertEqual(dg.DatasetGenerator.NUM_EVAL_COUNTRIES, len(test))
            
            train = set(train)
            dev = set(dev)
            test = set(test)

            # CHECK: the evaluation sets contain the correct number of elements
            self.assertEqual(dg.DatasetGenerator.NUM_EVAL_COUNTRIES, len(dev))
            self.assertEqual(dg.DatasetGenerator.NUM_EVAL_COUNTRIES, len(test))
            
            # CHECK: the split comprises all countries
            self.assertEqual(set(self.data.keys()), train | dev | test)
            
            # CHECK: the sets are disjoint
            self.assertFalse(train & dev)
            self.assertFalse(train & test)
            self.assertFalse(dev & test)
            
            # CHECK: every country in an evaluation set has a neighbor in the training set
            for c in itertools.chain(dev, test):
                self.assertTrue(train & set(self.data[c].neighbors))
