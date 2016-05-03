# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# attribute_selection.py
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.converters as converters
import weka.attribute_selection as attribute_selection
import wekatests.tests.weka_test as weka_test


class TestAttributeSelection(weka_test.WekaTest):

    def test_instantiations(self):
        """
        Tests instantiating classes.
        """
        cname = "weka.attributeSelection.BestFirst"
        options = ["-D", "1", "-N", "5"]
        search = attribute_selection.ASSearch(classname=cname, options=options)
        self.assertIsNotNone(search, msg="Search should not be None: " + cname + "/" + str(options))
        self.assertEqual(cname, search.classname, msg="Classnames differ!")

        cname = "weka.attributeSelection.CfsSubsetEval"
        options = ["-P", "1", "-E", "1"]
        evaluation = attribute_selection.ASEvaluation(classname=cname, options=options)
        self.assertIsNotNone(evaluation, msg="Evaluation should not be None: " + cname + "/" + str(options))
        self.assertEqual(cname, evaluation.classname, msg="Classnames differ!")

        attsel = attribute_selection.AttributeSelection()
        self.assertIsNotNone(search, msg="AttributeSelection should not be None!")

        attsel.search(search)
        attsel.evaluator(evaluation)

    def test_capabilities(self):
        """
        Tests the capabilities.
        """
        cname = "weka.attributeSelection.CfsSubsetEval"
        options = ["-P", "1", "-E", "1"]
        evaluation = attribute_selection.ASEvaluation(classname=cname, options=options)
        self.assertIsNotNone(evaluation, msg="Evaluation should not be None: " + cname + "/" + str(options))
        self.assertEqual(cname, evaluation.classname, msg="Classnames differ!")

        caps = evaluation.capabilities
        self.assertIsNotNone(caps, msg="Capabilities are None!")

    def test_attribute_selection(self):
        """
        Tests attribute selection.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.attributeSelection.BestFirst"
        options = ["-D", "1", "-N", "5"]
        search = attribute_selection.ASSearch(classname=cname, options=options)
        self.assertIsNotNone(search, msg="Search should not be None: " + cname + "/" + str(options))

        cname = "weka.attributeSelection.CfsSubsetEval"
        options = ["-P", "1", "-E", "1"]
        evaluation = attribute_selection.ASEvaluation(classname=cname, options=options)
        self.assertIsNotNone(evaluation, msg="Evaluation should not be None: " + cname + "/" + str(options))

        attsel = attribute_selection.AttributeSelection()
        self.assertIsNotNone(search, msg="AttributeSelection should not be None!")

        attsel.search(search)
        attsel.evaluator(evaluation)
        attsel.select_attributes(data)
        self.assertEqual(9, attsel.number_attributes_selected, msg="number_attributes_selected differs")
        self.assertEqual([0, 4, 8, 11, 12, 19, 24, 32, 33, 38], attsel.selected_attributes.tolist(), msg="selected_attributes differ")
        self.assertGreater(len(attsel.results_string), 0, msg="results_string should get produced")

    def test_reduce(self):
        """
        Tests reducing of attributes.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.attributeSelection.BestFirst"
        options = ["-D", "1", "-N", "5"]
        search = attribute_selection.ASSearch(classname=cname, options=options)
        self.assertIsNotNone(search, msg="Search should not be None: " + cname + "/" + str(options))

        cname = "weka.attributeSelection.CfsSubsetEval"
        options = ["-P", "1", "-E", "1"]
        evaluation = attribute_selection.ASEvaluation(classname=cname, options=options)
        self.assertIsNotNone(evaluation, msg="Evaluation should not be None: " + cname + "/" + str(options))

        attsel = attribute_selection.AttributeSelection()
        self.assertIsNotNone(search, msg="AttributeSelection should not be None!")

        attsel.search(search)
        attsel.evaluator(evaluation)
        attsel.select_attributes(data)
        reduced = attsel.reduce_dimensionality(data)
        self.assertEqual(attsel.number_attributes_selected + 1, reduced.num_attributes, msg="number of attributes differs")
        self.assertEqual(data.num_instances, reduced.num_instances, msg="number of rows differs")

    def test_ranking(self):
        """
        Tests ranking of attributes.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        search = attribute_selection.ASSearch(classname="weka.attributeSelection.Ranker", options=["-N", "-1"])
        self.assertIsNotNone(search, msg="Search should not be None!")

        evaluation = attribute_selection.ASEvaluation("weka.attributeSelection.InfoGainAttributeEval")
        self.assertIsNotNone(evaluation, msg="Evaluation should not be None!")

        attsel = attribute_selection.AttributeSelection()
        self.assertIsNotNone(attsel, msg="AttributeSelection should not be None!")

        attsel.ranking(True)
        attsel.folds(2)
        attsel.crossvalidation(True)
        attsel.seed(42)
        attsel.search(search)
        attsel.evaluator(evaluation)
        attsel.select_attributes(data)

        self.assertGreater(len(str(attsel.ranked_attributes)), 0, msg="results_string should get produced")
        self.assertGreater(len(attsel.results_string), 0, msg="results_string should get produced")


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestAttributeSelection)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
