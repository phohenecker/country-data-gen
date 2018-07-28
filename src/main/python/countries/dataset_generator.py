# -*- coding: utf-8 -*-


import collections
import itertools
import os
import random
import re
import typing

import insanity
import unidecode

from reldata import data_context as dc
from reldata.data import class_membership
from reldata.data import individual
from reldata.data import individual_factory as ind_fac
from reldata.data import knowledge_graph as kg
from reldata.data import triple
from reldata.io import kg_writer
from reldata.vocab import class_type_factory as ctf
from reldata.vocab import relation_type_factory as rtf

from countries import country
from countries import problem_setting as ps
from countries import vocabulary as voc
from countries.asp import base_solver
from countries.asp import literal


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
    
    MAX_ATTEMPTS = 100
    """int: The maximum number of attempts for generating a dataset."""
    
    NEIGHBOR_OF_PREDICATE = "neighborOf"
    """str: The predicate symbol that is used to represent the neighbor-of relation."""
    
    NUM_EVAL_COUNTRIES = 20
    """int: The number of countries to retain for each evaluation set, i.e., dev and test."""
    
    PROBLEM_S1 = ps.ProblemSetting.S1.value
    """str: An identifier for the first of the considered problem settings."""

    PROBLEM_S2 = ps.ProblemSetting.S2.value
    """str: An identifier for the second of the considered problem settings."""

    PROBLEM_S3 = ps.ProblemSetting.S3.value
    """str: An identifier for the third of the considered problem settings."""
    
    #  CONSTRUCTOR  ####################################################################################################
    
    def __init__(
            self,
            data: typing.Dict[str, country.Country],
            problem_setting: str,
            solver: base_solver.BaseSolver,
            ontology_path: str,
            class_facts: bool
    ):
        """Creates a new instance of ``DataGenerator`` for creating datasets from the provided data.
        
        Args:
            data (collections.OrderedDict): The data to generate datasets form. This is supposed to map country names to
                lists of neighbors, given in terms of the same names.
            problem_setting (str): The considered problem setting.
            solver (:class:`base_solver.BaseSolver`): The ASP solver to use.
            ontology_path (str): The path to the ASP program that describes the used ontology.
            class_facts (bool): Indicates whether to include class facts in generated samples.
        """
        # sanitize args
        insanity.sanitize_type("data", data, collections.OrderedDict)
        problem_setting = str(problem_setting)
        insanity.sanitize_value("problem_setting", problem_setting, [self.PROBLEM_S1, self.PROBLEM_S2, self.PROBLEM_S3])
        insanity.sanitize_type("solver", solver, base_solver.BaseSolver)
        ontology_path = str(ontology_path)
        if not os.path.isfile(ontology_path):
            raise ValueError(
                    "The provided <ontology_path> does not refer to an existing file: '{}'!".format(ontology_path)
            )
        
        # define attributes
        self._class_facts = bool(class_facts)    # indicates whether to include class facts in samples
        self._classes = {}                       # maps class names to individuals
        self._data = data                        # the provided data as dict from country names to Country objects
        self._ontology_path = ontology_path      # the ASP program that describes the ontology
        self._problem_setting = problem_setting  # the considered version of the reasoning problem
        self._regions = None                     # maps region names to lists of (names of) subregions
        self._relations = {}                     # maps relation names to individuals
        self._solver = solver                    # the used ASP solver
        
        # fix the names of countries, regions, and subregions in the data (DLV expects camel case)
        self._data = {self._fix_name(k): v for k, v in self._data.items()}
        for c in self._data.values():
            c.name = self._fix_name(c.name)
            c.region = self._fix_name(c.region)
            c.subregion = None if c.subregion is None else self._fix_name(c.subregion)
            c.neighbors = [self._fix_name(n) for n in c.neighbors]
        
        # extract regions/subregions from the data
        regions = {}
        for c in self._data.values():
            if c.region not in regions:
                regions[c.region] = set()
            if c.subregion is not None and c.subregion not in regions[c.region]:
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
    
    def _add_literal_to_kg(
            self,
            sample: kg.KnowledgeGraph,
            individuals: typing.Dict[str, individual.Individual],
            lit: literal.Literal,
            inferred: bool=False,
            prediction: bool=False
    ) -> None:
        """Adds a literal to a knowledge graph.
        
        Args:
            sample (kg.KnowledgeGraph): The knowledge graph to add the literal to.
            individuals (dict[str, individual.Individual): Maps names to individuals of ``sample``.
            lit (:class:`literal.Literal`) The literal to add.
            inferred (bool, optional): Indicates whether the literal has been inferred, which is ``False`` by default.
            prediction (bool, optional): Indicates whether the literal is a prediction target, which is ``False`` by
                default.
        """
        if len(lit.terms) == 1:
            individuals[lit.terms[0]].classes.add(
                    class_membership.ClassMembership(
                            self._classes[lit.predicate],
                            lit.positive,
                            inferred=inferred,
                            prediction=prediction
                    )
            )
        else:
            sample.triples.add(
                    triple.Triple(
                            individuals[lit.terms[0]],
                            self._relations[lit.predicate],
                            individuals[lit.terms[1]],
                            positive=lit.positive,
                            inferred=inferred,
                            prediction=prediction
                    )
            )
    
    @staticmethod
    def _fix_name(name: str) -> str:
        """Turns the provided name into one that is compatible with DLV.
        
        DLV expects names to be alphanumeric and in camel case.
        
        Args:
            name (str): The name to fix.
        
        Returns:
            str: A camel case version of ``name``.
        """
        # remove accents
        name = unidecode.unidecode(name)
        
        # remove commas, quotes, apostrophes, and parentheses
        name = re.sub(r"[,\"'()]", "", name)
        
        # make name camel case
        words = re.split("[ -]", name.lower())
        valid_name = ""
        for w in words:
            if valid_name:
                valid_name += w[0].upper() + w[1:]
            else:
                valid_name = w
        
        return valid_name
    
    @dc.new_context
    def _generate_sample(
            self,
            spec_countries: typing.List[str],
            inf_countries: typing.List[str]=None,
            minimal: bool=False
    ) -> kg.KnowledgeGraph:
        """Generates a single training samples based on the provided data.
        
        The arg ``spec_countries`` contains the names of all countries that are supposed to be specified, i.e., fully
        known, in the dataset to create, and ``inf_countries`` indicates the names of those whose regions are to be
        inferred. If ``inf_countries`` is not provided, however, then the prediction targets are chosen randomly from
        ``spec_countries``.
        
        Args:
            spec_countries (list[str]): All countries whose regions are specified.
            inf_countries (list[str], optional): Those countries, whose regions are to be inferred.
            minimal (bool, optional): Specifies whether to generate a minimal sample, i.e., one that contains inferences
                and predictions for target countries only. This is ``False``, by default.
        
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
        
        # a dict that maps names to individual objects
        individuals = {}

        # create variables for storing facts
        class_facts = set()     # all (positive) class memberships (negative ones are inferred from these)
        neighbor_facts = set()  # all facts about (positive) neighbor-of relations (negative ones are inferred)
        location_facts = set()  # the part of the (positive) located-in facts to infer the remaining ones from
        all_locations = set()   # all (positive) located-in relations (negatives ones are inferred from these)
        
        # create individuals for all regions/subregions
        for region in itertools.chain(*((r, *s) for r, s in self._regions.items())):
            individuals[region] = ind_fac.IndividualFactory.create_individual(region)
            sample.individuals.add(individuals[region])

        # create literals that describe the existing regions and subregions as well as the relations among them
        for r, subregions in self._regions.items():
            class_facts.add(literal.Literal(voc.CLASS_REGION, [r]))
            for s in subregions:
                class_facts.add(literal.Literal(voc.CLASS_SUBREGION, [s]))
                loc_lit = literal.Literal(voc.RELATION_LOCATED_IN, [s, r])
                location_facts.add(loc_lit)
                all_locations.add(loc_lit)
        
        # create individuals for all countries
        for c in countries:
            individuals[c] = ind_fac.IndividualFactory.create_individual(c)
            sample.individuals.add(individuals[c])
        
        # create literals for (countries') located-in and neighbor-of relationships
        for cou_name in countries:
        
            # fetch the current country's region and subregion
            r = self._data[cou_name].region
            s = self._data[cou_name].subregion
            
            # create literals that describe the country as well as the relation to its region/subregion
            cou_lit = literal.Literal(voc.CLASS_COUNTRY, [cou_name])
            reg_lit = literal.Literal(voc.RELATION_LOCATED_IN, [cou_name, r])
            sub_lit = None if s is None else literal.Literal(voc.RELATION_LOCATED_IN, [cou_name, s])
            class_facts.add(cou_lit)
            all_locations.add(reg_lit)
            if sub_lit is not None:
                all_locations.add(sub_lit)
            
            # determine whether the located-in predicates should be added to the list of provided facts
            if self._problem_setting == self.PROBLEM_S1:
                if sub_lit is not None:            # subregion is provided for all countries
                    location_facts.add(sub_lit)
                if cou_name not in inf_countries:  # region is not provided for target countries
                    location_facts.add(reg_lit)
            elif self._problem_setting == self.PROBLEM_S2:
                if cou_name not in inf_countries:  # neither region nor subregion are provided for target countries
                    location_facts.add(reg_lit)
                    if sub_lit is not None:
                        location_facts.add(sub_lit)
            else:
                if cou_name not in inf_countries and cou_name not in inf_neighbors:  # region is neither provided for
                    location_facts.add(reg_lit)                                      # for targets nor their neighbors
                if cou_name not in inf_countries and sub_lit is not None:            # subregion is not provided for
                    location_facts.add(sub_lit)                                      # target countries
            
            # iterate over all neighbors of the current country, and add according neighbor-of literals
            for n in self._data[cou_name].neighbors:
                if n in countries:  # -> important, because not all of the countries in self._data might be used
                    neighbor_facts.add(literal.Literal(self.NEIGHBOR_OF_PREDICATE, [cou_name, n]))
                    neighbor_facts.add(literal.Literal(self.NEIGHBOR_OF_PREDICATE, [n, cou_name]))
        
        # compute all inferences that are possible based on the restricted data
        input_facts = list(itertools.chain(neighbor_facts, location_facts))
        if self._class_facts:
            input_facts += class_facts
        answer_set = self._solver.run(self._ontology_path, input_facts)
        
        # add all facts to the sample
        for f in list(sorted(answer_set.facts, key=lambda x: str(x))):
            self._add_literal_to_kg(sample, individuals, f)
        
        # add all inferences ot the sample
        for i in list(sorted(answer_set.inferences, key=lambda x: str(x))):
            if (
                    not minimal or
                    i.predicate == "region" or
                    i.predicate == "subregion" or
                    (len(i.terms) == 1 and i.terms[0] in inf_countries) or
                    (len(i.terms) == 2 and (i.terms[0] in inf_countries or i.terms[1] in inf_countries))
            ):
                self._add_literal_to_kg(sample, individuals, i, inferred=True)
        
        # compute perfect knowledge
        perfect_knowledge = set(
                self._solver.run(
                        self._ontology_path,
                        itertools.chain(class_facts, neighbor_facts, all_locations)
                )
        )
        
        # determine all information that was neither provided nor inferred
        missing_knowledge = list(sorted(perfect_knowledge - set(answer_set), key=lambda x: str(x)))

        # add missing knowledge as prediction targets to the sample
        for p in missing_knowledge:
            if (
                    not minimal or
                    p.predicate == "region" or
                    p.predicate == "subregion" or
                    (len(p.terms) == 1 and p.terms[0] in inf_countries) or
                    (len(p.terms) == 2 and (p.terms[0] in inf_countries or p.terms[1] in inf_countries))
            ):
                self._add_literal_to_kg(sample, individuals, p, prediction=True)
        
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
        
    def generate_datasets(
            self,
            num_datasets: int,
            num_training_samples: int,
            output_dir: str
    ) -> None:
        """Generates datasets from the data that was provided to this instance of ``DatasetGenerator`, and writes them
        to disk.
        
        Args:
            num_datasets (int): The total number of datasets to create.
            num_training_samples (int): The number of training samples to create for each dataset.
            output_dir (str): The path of the output directory.
        """
        # sanitize args
        insanity.sanitize_type("num_datasets", num_datasets, int)
        insanity.sanitize_range("num_datasets", num_datasets, minimum=1)
        insanity.sanitize_type("num_training_samples", num_training_samples, int)
        insanity.sanitize_range("num_training_samples", num_training_samples, minimum=1)

        # create patterns for the names of the directories that are created for the single datasets and for
        # the base names of training samples
        output_dir_pattern = "{:0" + str(len(str(num_datasets - 1))) + "d}"
        sample_filename_pattern = "{:0" + str(len(str(num_training_samples - 1))) + "d}"
        
        for dataset_idx in range(num_datasets):
            
            print("generating dataset #{}...".format(dataset_idx))

            # assemble needed paths
            ds_output_dir = os.path.join(output_dir, output_dir_pattern.format(dataset_idx))
            train_dir = os.path.join(ds_output_dir, "train")
            dev_dir = os.path.join(ds_output_dir, "dev")
            test_dir = os.path.join(ds_output_dir, "test")

            # create folder structure for storing the current dataset
            if not os.path.isdir(ds_output_dir):
                os.mkdir(ds_output_dir)
            if not os.path.isdir(train_dir):
                os.mkdir(train_dir)
            if not os.path.isdir(dev_dir):
                os.mkdir(dev_dir)
            if not os.path.isdir(test_dir):
                os.mkdir(test_dir)
        
            # split countries into train/dev/test
            train, dev, test = self._split_countries()

            # write selected dev+test countries to disk
            with open(os.path.join(ds_output_dir, "countries.dev.txt"), "w") as f:
                for c in dev:
                    f.write("{}\n".format(c))
            with open(os.path.join(ds_output_dir, "countries.test.txt"), "w") as f:
                for c in test:
                    f.write("{}\n".format(c))
            
            # create training samples + write them to disk
            for sample_idx in range(num_training_samples):
                print("generating training sample #{}...".format(sample_idx))
                sample = self._generate_sample(train)
                kg_writer.KgWriter.write(sample, train_dir, sample_filename_pattern.format(sample_idx))
            
            # create evaluation sample + write it to disk
            print("generating dev sample... ")
            dev_sample = self._generate_sample(train, inf_countries=dev, minimal=True)
            kg_writer.KgWriter.write(dev_sample, dev_dir, "dev")

            # create test sample + write it to disk
            print("generating test sample...")
            test_sample = self._generate_sample(train, inf_countries=test, minimal=True)
            kg_writer.KgWriter.write(test_sample, test_dir, "test")
            
            # print statistics about test sample
            num_spec = len([t for t in test_sample.triples if not t.inferred])
            num_inf = len([t for t in test_sample.triples if t.inferred])
            print("number triples in test sample: {} ({} spec / {} inf)".format(num_spec + num_inf, num_spec, num_inf))

            print("OK\n")
