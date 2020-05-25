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

# filters.py
# Copyright (C) 2014-2020 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.converters as converters
import weka.core.dataset as dataset
import weka.filters as filters
import wekatests.tests.weka_test as weka_test
import weka.attribute_selection as attsel


class TestFilters(weka_test.WekaTest):

    def test_instantiate_classifier(self):
        """
        Tests the instantiation of several classifier classes.
        """
        cname = "weka.filters.unsupervised.attribute.Remove"
        options = None
        flter = filters.Filter(classname=cname, options=["-R", "1,3"])
        self.assertIsNotNone(flter, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, flter.classname, msg="Classnames differ!")

    def test_make_copy(self):
        """
        Tests the make_copy class method.
        """
        cname = "weka.filters.unsupervised.attribute.Remove"
        options = None
        flter = filters.Filter(classname=cname, options=["-R", "1,3"])
        self.assertIsNotNone(flter, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, flter.classname, msg="Classnames differ!")

        flter2 = filters.Filter.make_copy(flter)
        self.assertIsNotNone(flter2, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, flter2.classname, msg="Classnames differ!")

    def test_capabilities(self):
        """
        Tests the capabilities.
        """
        cname = "weka.classifiers.trees.J48"
        options = None
        flter = filters.Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1,3"])
        self.assertIsNotNone(flter, msg="Failed to instantiate: " + cname + "/" + str(options))

        caps = flter.capabilities
        self.assertIsNotNone(caps, msg="Capabilities are None!")

    def test_batch_filtering(self):
        """
        Tests the Filter.filter method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)

        flter = filters.Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1,3"])
        flter.inputformat(data)
        filtered = flter.filter(data)
        self.assertEqual(data.num_attributes - 2, filtered.num_attributes, msg="Number of attributes differ")
        self.assertEqual(data.num_instances, filtered.num_instances, msg="Number of instances differ")

        # multple files
        data = loader.load_file(self.datafile("reutersTop10Randomized_1perc_shortened-train.arff"))
        self.assertIsNotNone(data)
        data2 = loader.load_file(self.datafile("reutersTop10Randomized_1perc_shortened-test.arff"))
        self.assertIsNotNone(data2)

        flter = filters.Filter(classname="weka.filters.unsupervised.attribute.StringToWordVector")
        flter.inputformat(data)
        filtered = flter.filter([data, data2])
        self.assertIsNone(filtered[0].equal_headers(filtered[1]), msg="Headers should be compatible")

    def test_incremental_filtering(self):
        """
        Tests the Filter.input/output methods.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)

        flter = filters.Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1,3"])
        flter.inputformat(data)
        filtered = flter.outputformat()
        self.assertIsNotNone(filtered)
        self.assertTrue(isinstance(filtered, dataset.Instances), msg="Should be Instances object")

        for inst in data:
            flter.input(inst)
            finst = flter.output()
            filtered.add_instance(finst)

        self.assertEqual(data.num_attributes - 2, filtered.num_attributes, msg="Number of attributes differ")
        self.assertEqual(data.num_instances, filtered.num_instances, msg="Number of instances differ")

    def test_attributeselectionfilter(self):
        """
        Tests the AttributeSelection filter class.
        """
        fas = filters.AttributeSelection()
        fas.evaluator = attsel.ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval", options=["-P", "1", "-E", "1"])
        fas.search = attsel.ASSearch(classname="weka.attributeSelection.GreedyStepwise", options=["-B", "-T", "-1.7E308", "-N", "-1", "-num-slots", "1"])
        self.assertEqual("weka.attributeSelection.CfsSubsetEval -P 1 -E 1", fas.evaluator.to_commandline(), msg="evaluator command-lines differs")
        self.assertEqual("weka.attributeSelection.GreedyStepwise -B -T -1.7E308 -N -1 -num-slots 1", fas.search.to_commandline(), msg="search command-lines differs")

def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestFilters)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
