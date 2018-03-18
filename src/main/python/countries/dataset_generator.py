# -*- coding: utf-8 -*-


import collections
import itertools
import random
import typing

import insanity

from reldata import data_context as dc
from reldata.data import class_membership
from reldata.data import individual_factory as ind_fac
from reldata.data import knowledge_graph as kg
from reldata.data import triple
from reldata.vocab import class_type_factory as ctf
from reldata.vocab import relation_type_factory as rtf

from countries import country
from countries import dataset
from countries import problem_setting as ps
from countries import vocabulary as voc


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
__date__ = "Mar 15, 2018"
__maintainer__ = "Patrick Hohenecker"
__email__ = "mail@paho.at"
__status__ = "Development"


class DatasetGenerator(object):
    """This class implements the actual process of generating a dataset."""
    
    NUM_EVAL_COUNTRIES = 20
    """int: The number of countries to retain for each evaluation set, i.e., dev and test."""
    
    MAX_ATTEMPTS = 100
    """int: The maximum number of attempts for generating a dataset."""
    
    PROBLEM_S1 = ps.ProblemSetting.S1.value
    """str: An identifier for the first of the considered problem settings."""

    PROBLEM_S2 = ps.ProblemSetting.S2.value
    """str: An identifier for the second of the considered problem settings."""

    PROBLEM_S3 = ps.ProblemSetting.S3.value
    """str: An identifier for the third of the considered problem settings."""
    
    #  CONSTRUCTOR  ####################################################################################################
    
    def __init__(self, data: typing.Dict[str, country.Country], problem_setting: str):
        """Creates a new instance of ``DataGenerator`` for creating datasets from the provided data.
        
        Args:
            data (collections.OrderedDict): The data to generate datasets form. This is supposed to map country names to
                lists of neighbors, given in terms of the same names.
            problem_setting (str): The considered problem setting.
        """
        # sanitize args
        insanity.sanitize_type("data", data, collections.OrderedDict)
        problem_setting = str(problem_setting)
        insanity.sanitize_value("problem_setting", problem_setting, [self.PROBLEM_S1, self.PROBLEM_S2, self.PROBLEM_S3])
        
        # define attributes
        self._classes = {}                       # maps class names to individuals
        self._data = data                        # the provided data as dict from country names to Country objects
        self._problem_setting = problem_setting  # the considered version of the reasoning problem
        self._regions = None                     # maps region names to lists of (names of) subregions
        self._relations = {}                     # maps relation names to individuals
        
        # extract regions/subregions from the data
        regions = {}
        for c in self._data.values():
            if c.region not in regions:
                regions[c.region] = set()
            if c.subregion not in regions[c.region]:
                regions[c.region].add(c.subregion)
        
        # sort regions/subregions alphabetically
        self._regions = collections.OrderedDict(
                (r, list(x for x in sorted(s) if x is not None))
                for r, s in sorted(regions.items(), key=lambda x: x[0])
        )
        
        # prepare all reusable parts of any (subsequently) generated sample knowledge graph
        with dc.DataContext():
            
            # create all classes
            self._classes[voc.CLASS_COUNTRY] = ctf.ClassTypeFactory.create_class(voc.CLASS_COUNTRY)
            self._classes[voc.CLASS_REGION] = ctf.ClassTypeFactory.create_class(voc.CLASS_REGION)
            self._classes[voc.CLASS_SUBREGION] = ctf.ClassTypeFactory.create_class(voc.CLASS_SUBREGION)
            
            # create all relations
            self._relations[voc.RELATION_LOCATED_IN] = rtf.RelationTypeFactory.create_relation(voc.RELATION_LOCATED_IN)
            self._relations[voc.RELATION_NEIGHBOR_OF] = rtf.RelationTypeFactory.create_relation(
                    voc.RELATION_NEIGHBOR_OF
            )
    
    #  METHODS  ########################################################################################################
    
    @dc.new_context
    def _generate_sample(
            self,
            spec_countries: typing.List[str],
            inf_countries: typing.List[str]=None
    ) -> kg.KnowledgeGraph:
        """Generates a single training samples based on the provided data.
        
        The arg ``spec_countries`` contains the names of all countries that are supposed to be specified, i.e., fully
        known, in the dataset to create, and ``inf_countries`` indicates the names of those whose regions are to be
        inferred. If ``inf_countries`` is not provided, however, then the prediction targets are chosen randomly from
        ``spec_countries``.
        
        Args:
            spec_countries (list[str]): All countries whose regions are specified.
            inf_countries (list[str], optional): Those countries, whose regions are to be inferred.
        
        Returns:
            kg.KnowledgeGraph: The created training sample.
        """
        # randomly shuffle countries
        countries = spec_countries[:]
        if inf_countries:
            countries += inf_countries
        random.shuffle(countries)
        
        # (randomly) choose prediction targets if not provided
        if inf_countries:
            inf_countries = set(inf_countries)
        else:
            inf_countries = set(countries[-self.NUM_EVAL_COUNTRIES:])
        
        # determine all countries that are neighbors of a prediction target (but not targets by themselves)
        inf_neighbors = set()
        for c in inf_countries:
            inf_neighbors |= set(self._data[c].neighbors)
        inf_neighbors -= set(inf_countries)
    
        # create new knowledge graph and add vocabulary
        sample = kg.KnowledgeGraph()
        sample.classes.add_all(self._classes.values())
        sample.relations.add_all(self._relations.values())
        
        # create individuals for all regions/subregions
        regions = {}  # used to store individuals for regions, maps from names to individuals
        for region in itertools.chain(*((r, *s) for r, s in self._regions.items())):
            regions[region] = ind_fac.IndividualFactory.create_individual(region.replace(" ", "-"))
        sample.individuals.add_all(regions.values())
        
        # specify classes for all regions
        for region_name, region_ind in regions.items():
            
            # determine whether the current one is a region or a subregion
            is_region = region_name in self._regions
            
            region_ind.classes.add(
                    class_membership.ClassMembership(
                            self._classes[voc.CLASS_REGION],  # class
                            is_region,                        # is_member
                            not is_region                     # inferred
                    )
            )
            region_ind.classes.add(
                    class_membership.ClassMembership(
                            self._classes[voc.CLASS_SUBREGION],  # class
                            not is_region,                       # is_member
                            is_region                            # inferred
                    )
            )
            region_ind.classes.add(
                    class_membership.ClassMembership(
                            self._classes[voc.CLASS_COUNTRY],  # class
                            False,                             # is_member
                            True                               # inferred
                    )
            )
        
        # create triples for subregion relationships
        for r, subregions in self._regions.items():
            for s in subregions:
                sample.triples.add(
                        triple.Triple(
                                regions[s],                                # s
                                self._relations[voc.RELATION_LOCATED_IN],  # p
                                regions[r],                                # o
                                True,                                      # positive
                                False                                      # inferred
                        )
                )
        
        # create individuals for all countries, maps names to individuals
        countries = collections.OrderedDict((c, ind_fac.IndividualFactory.create_individual(c)) for c in countries)
        sample.individuals.add_all(countries.values())

        # specify classes for all regions
        for cou in countries.values():
            cou.classes.add(
                    class_membership.ClassMembership(
                            self._classes[voc.CLASS_COUNTRY],  # class
                            True,                              # is_member
                            False                              # inferred
                    )
            )
            cou.classes.add(
                    class_membership.ClassMembership(
                            self._classes[voc.CLASS_REGION],  # class
                            False,                            # is_member
                            True                              # inferred
                    )
            )
            cou.classes.add(
                    class_membership.ClassMembership(
                            self._classes[voc.CLASS_SUBREGION],  # class
                            False,                               # is_member
                            True                                 # inferred
                    )
            )
        
        all_located_in = set()   # used to store all positive located-in triples (as s-o-pairs of country names)
        all_neighbor_of = set()  # used to store all positive neighbor-of triples (as s-o-pairs of country names)
        
        # create triples for (countries') located-in and neighbor-of relationships
        for cou_name, cou_ind in countries.items():
        
            # fetch the countries region and subregion (as individuals)
            r = regions[self._data[cou_name].region]
            s = None if self._data[cou_name].subregion is None else regions[self._data[cou_name].subregion]

            # store the triples (for generating negatives later on)
            all_located_in.add((cou_name, self._data[cou_name].region))
            if s is not None:
                all_located_in.add((cou_name, self._data[cou_name].subregion))
            
            # add triples for located_in
            inferred = (
                    cou_name in inf_countries or
                    (self._problem_setting == self.PROBLEM_S3 and cou_name in inf_neighbors)
            )
            sample.triples.add(
                    triple.Triple(
                            cou_ind,                                   # s
                            self._relations[voc.RELATION_LOCATED_IN],  # p
                            r,                                         # o
                            True,                                      # positive
                            inferred                                   # inferred
                    )
            )
            if s is not None:
                inferred = cou_name in inf_countries and not self._problem_setting == self.PROBLEM_S1
                sample.triples.add(
                        triple.Triple(
                                cou_ind,                                   # s
                                self._relations[voc.RELATION_LOCATED_IN],  # p
                                s,                                         # o
                                True,                                      # positive
                                inferred                                   # inferred
                        )
                )
            
            # iterate over all neighbors of the current individual, and add an according neighbor_of triple
            for n in self._data[cou_name].neighbors:
                
                # ensure that the current neighbor is part of the generated dataset
                if n not in countries:
                    continue
                
                # store the triples (for generating negatives later on)
                all_neighbor_of.add((cou_name, n))
                
                # fetch the individual for the current neighbor
                n = countries[n]
                
                # add the triple
                sample.triples.add(
                        triple.Triple(
                                cou_ind,                                    # s
                                self._relations[voc.RELATION_NEIGHBOR_OF],  # p
                                n,                                          # o
                                True,                                       # positive
                                False                                       # inferred
                        )
                )
        
        # iterate over all country-region pairs, and add a negative located-in triple no positive was added before
        for cou_name, cou_ind in countries.items():
            for reg_name, reg_ind in regions.items():
                
                # check if the current country is located in the current region, and add a negative triple if not
                if (cou_name, reg_name) not in all_located_in:
    
                    # determine whether the triple is specified or inferred
                    if reg_name in self._regions:  # the current region is NOT a subregion
                        inferred = (
                                cou_name in inf_countries or
                                (self._problem_setting == self.PROBLEM_S3 and cou_name in inf_neighbors)
                        )
                    else:  # the current region IS a subregion
                        inferred = cou_name in inf_countries and self._problem_setting != self.PROBLEM_S1
                    
                    # add the triple
                    sample.triples.add(
                            triple.Triple(
                                    cou_ind,                                   # s
                                    self._relations[voc.RELATION_LOCATED_IN],  # p
                                    reg_ind,                                   # o
                                    False,                                     # positive
                                    inferred                                   # inferred
                            )
                    )
        
        # iterate over all pairs of countries, and add a negative neighbor-of triple if no positive was added before
        # for cou_name_1, cou_ind_1 in countries.items():
        #     for cou_name_2, cou_ind_2 in countries.items():
        #
        #         # check if the current individuals are no neighbors, and add a negative triple if not
        #         if (cou_name_1, cou_name_2) not in all_neighbor_of:
        #             sample.triples.add(
        #                     triple.Triple(
        #                             cou_ind_1,                                  # s
        #                             self._relations[voc.RELATION_NEIGHBOR_OF],  # p
        #                             cou_ind_2,                                  # o
        #                             False,                                      # positive
        #                             True                                        # inferred
        #                     )
        #             )
        
        # provide the created sample
        return sample

    def _split_countries(self) -> typing.Tuple[typing.List[str], typing.List[str], typing.List[str]]:
        """Splits the considered countries into training, dev, and test set.
        
        Returns:
            tuple: A triple of lists representing training, dev, and test countries.
        
        Raises:
            ValueError: If splitting failed :attr:`MAX_ATTEMPTS' times.
        """
        # try to split the countries (at most MAX_ATTEMPTS times)
        for a in range(self.MAX_ATTEMPTS):
            
            # fetch and shuffle all countries that have neighbors
            all_countries = list(sorted((n for n, c in self._data.items() if len(c.neighbors) > 0)))
            random.shuffle(all_countries)
            
            # split countries into train/dev/test
            dev = sorted(all_countries[:self.NUM_EVAL_COUNTRIES])
            test = sorted(all_countries[self.NUM_EVAL_COUNTRIES:2 * self.NUM_EVAL_COUNTRIES])

            # create set for storing used countries
            used_countries = set(itertools.chain(dev, test))
            
            # check whether each country in dev and test has a neighbor that has not been used yet
            for c in itertools.chain(dev, test):  # run through all countries in dev and test
                
                for neighbor in self._data[c].neighbors:  # run through all neighbors of the current country
                    
                    # if the current country has a neighbor in the test set -> we can stop checking it
                    if neighbor not in used_countries:  # -> neighbor will be part of the training set
                        break
                
                else:
                    # the current country has no neighbors in the test set -> the attempt failed
                    break
     
            else:
                # assemble and sort the training set
                train = all_countries[2 * self.NUM_EVAL_COUNTRIES:]
                train += [n for n, c in self._data.items() if len(c.neighbors) == 0]  # add countries without neighbors
                train.sort()
                
                # return the created split
                return train, dev, test
        
        # raise an error to signal that the maximum number of attempts was exceeded
        raise ValueError("{} attempts to split the countries into train/dev/test failed!".format(self.MAX_ATTEMPTS))
        
    def generate_datasets(self, num_datasets, num_training_samples) -> typing.List[dataset.Dataset]:
        """Generates datasets from the data that was provided to this instance of ``DatasetGenerator`.
        
        Args:
            num_datasets (int): The total number of datasets to create.
            num_training_samples (int): The number of training samples to create for each dataset.
        """
        # sanitize args
        insanity.sanitize_type("num_datasets", num_datasets, int)
        insanity.sanitize_range("num_datasets", num_datasets, minimum=1)
        insanity.sanitize_type("num_training_samples", num_training_samples, int)
        insanity.sanitize_range("num_training_samples", num_training_samples, minimum=1)
        
        datasets = []  # store the created datasets
        
        for _ in range(num_datasets):
        
            # split countries into train/dev/test
            train, dev, test = self._split_countries()
            
            # create training samples
            train_samples = [self._generate_sample(train) for _ in range(num_training_samples)]
            
            # create evaluation samples
            dev_sample = self._generate_sample(train, inf_countries=dev)
            test_sample = self._generate_sample(train, inf_countries=test)
            
            # create dataset
            datasets.append(dataset.Dataset(train_samples, dev_sample, test_sample))
            
            num_spec = len([t for t in test_sample.triples if not t.inferred])
            num_inf = len([t for t in test_sample.triples if t.inferred])
            print("# triples in test sample: {} ({} spec / {} inf)".format(num_spec + num_inf, num_spec, num_inf))
        
        return datasets
