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

# dataset.py
# Copyright (C) 2014-2019 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.dataset as dataset
import weka.core.converters as converters
import wekatests.tests.weka_test as weka_test
from weka.core.dataset import create_instances_from_lists, create_instances_from_matrices
from random import randint
import numpy as np


class TestDataset(weka_test.WekaTest):

    def test_attribute(self):
        """
        Tests the Attribute class.
        """
        name = "Num"
        att = dataset.Attribute.create_numeric(name)
        self.assertIsNotNone(att, "Failed to create attribute!")
        self.assertEqual(name, att.name, "Names differ")
        self.assertTrue(att.is_numeric)

        name = "Nom"
        att = dataset.Attribute.create_nominal(name, ["A", "B", "C"])
        self.assertIsNotNone(att, "Failed to create attribute!")
        self.assertEqual(name, att.name, "Names differ")
        self.assertTrue(att.is_nominal)

        name = "Dat1"
        att = dataset.Attribute.create_date(name)
        self.assertIsNotNone(att, "Failed to create attribute!")
        self.assertEqual(name, att.name, "Names differ")
        self.assertTrue(att.is_date)

        name = "Dat2"
        att = dataset.Attribute.create_date(name, formt="yyyy-MM-dd HH:mm")
        self.assertIsNotNone(att, "Failed to create attribute!")
        self.assertEqual(name, att.name, "Names differ")
        self.assertTrue(att.is_date)

        name = "Str"
        att = dataset.Attribute.create_string(name)
        self.assertIsNotNone(att, "Failed to create attribute!")
        self.assertEqual(name, att.name, "Names differ")
        self.assertTrue(att.is_string)

    def test_attributestats(self):
        """
        Tests the AttributeStats class.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data, msg="Failed to load data!")

        stats = data.attribute_stats(2)
        self.assertIsNotNone(stats, msg="Failed to obtain stats!")
        self.assertEqual(8, stats.distinct_count, "distinct_count differs")
        self.assertEqual(898, stats.int_count, "int_count differs")
        self.assertEqual(0, stats.missing_count, "missing_count differs")
        self.assertEqual([86, 256, 440, 0, 51, 20, 10, 19, 16], stats.nominal_counts.tolist(), "nominal_counts differs")
        self.assertEqual([86, 256, 440, 0, 51, 20, 10, 19, 16], stats.nominal_weights.tolist(), "nominal_weights differs")
        self.assertEqual(898, stats.total_count, "total_count differs")
        self.assertEqual(0, stats.unique_count, "unique_count differs")

    def test_stats(self):
        """
        Tests the Stats class.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data, msg="Failed to load data!")

        stats = data.attribute_stats(3)
        numstats = stats.numeric_stats
        self.assertAlmostEqual(898, numstats.count, places=3, msg="count differs")
        self.assertAlmostEqual(70, numstats.max, places=3, msg="max differs")
        self.assertAlmostEqual(3.635, numstats.mean, places=3, msg="mean differs")
        self.assertAlmostEqual(0.0, numstats.min, places=3, msg="min differs")
        self.assertAlmostEqual(13.717, numstats.stddev, places=3, msg="stddev differs")
        self.assertAlmostEqual(3264, numstats.sum, places=3, msg="sum differs")
        self.assertAlmostEqual(180636, numstats.sumsq, places=3, msg="sumsq differs")

    def test_instance(self):
        """
        Tests the Instance class.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.ORIG.arff"))
        self.assertIsNotNone(data, msg="Failed to load data!")

        inst = data.get_instance(0)
        self.assertEqual(39, inst.num_attributes, msg="num_attributes differs")
        self.assertEqual(-1, data.class_index, msg="class_index differs")

        data.class_index = data.num_attributes - 1
        self.assertEqual(38, data.class_index, msg="class_index differs")

        data.class_is_first()
        self.assertEqual(0, data.class_index, msg="class_index differs")

        data.class_is_last()
        self.assertEqual(38, data.class_index, msg="class_index differs")

        self.assertIsNotNone(inst.dataset, msg="Dataset reference should not be None!")
        self.assertTrue(inst.has_missing(), msg="Should have missing values")
        self.assertTrue(inst.is_missing(0), msg="First value should be missing")
        self.assertFalse(inst.is_missing(1), msg="Second value should not be missing")

        self.assertEqual("C", inst.get_string_value(1), msg="string value differs")
        inst.set_string_value(1, "H")
        self.assertEqual("H", inst.get_string_value(1), msg="string value differs")

        self.assertEqual(8, inst.get_value(3), msg="numeric value differs")
        inst.set_value(3, 6.3)
        self.assertEqual(6.3, inst.get_value(3), msg="numeric value differs")

        self.assertEqual(1, inst.weight, msg="weight should be 1")
        inst.weight = 0.5
        self.assertEqual(0.5, inst.weight, msg="weights differ")

        values = [1.0, 2.0, 3.0]
        inst = dataset.Instance.create_instance(values, classname="weka.core.DenseInstance")
        self.assertEqual(3, inst.num_attributes, msg="#attributes differ")
        self.assertEqual(1.0, inst.get_value(0), msg="value at #" + str(0) + " differs")
        self.assertEqual(2.0, inst.get_value(1), msg="value at #" + str(1) + " differs")
        self.assertEqual(3.0, inst.get_value(2), msg="value at #" + str(2) + " differs")

        values = [0.0, 2.0, 0.0]
        inst = dataset.Instance.create_instance(values, classname="weka.core.SparseInstance")
        self.assertEqual(3, inst.num_attributes, msg="#attributes differ")
        self.assertEqual(0.0, inst.get_value(0), msg="value at #" + str(0) + " differs")
        self.assertEqual(2.0, inst.get_value(1), msg="value at #" + str(1) + " differs")
        self.assertEqual(0.0, inst.get_value(2), msg="value at #" + str(2) + " differs")

        values = [(1, 2.0)]
        inst = dataset.Instance.create_sparse_instance(values, 3, classname="weka.core.SparseInstance")
        self.assertEqual(3, inst.num_attributes, msg="#attributes differ")
        self.assertEqual(0.0, inst.get_value(0), msg="value at #" + str(0) + " differs")
        self.assertEqual(2.0, inst.get_value(1), msg="value at #" + str(1) + " differs")
        self.assertEqual(0.0, inst.get_value(2), msg="value at #" + str(2) + " differs")

    def test_instances(self):
        """
        Tests the Instances class.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data, msg="Failed to load data!")
        self.assertFalse(data.has_class(), msg="Should not have class set!")

        count = 0
        for i in data:
            count += 1
        self.assertEqual(898, count, msg="Number of rows differs!")

        count = 0
        for i in data.attributes():
            count += 1
        self.assertEqual(39, count, msg="Number of attributes differs!")

        self.assertEqual(898, data.num_instances, msg="num_instances differs")
        self.assertEqual(39, data.num_attributes, msg="num_attributes differs")
        self.assertEqual(-1, data.class_index, msg="class_index differs")

        data.class_index = data.num_attributes - 1
        self.assertEqual(38, data.class_index, msg="class_index differs")
        self.assertEqual(38, data.class_attribute.index, msg="class_index differs")

        data.class_is_first()
        self.assertEqual(0, data.class_index, msg="class_index differs")
        self.assertTrue(data.has_class(), msg="Should have class set!")

        data.class_is_last()
        self.assertEqual(38, data.class_index, msg="class_index differs")
        self.assertTrue(data.has_class(), msg="Should have class set!")

        att = data.attribute(0)
        self.assertIsNotNone(att, msg="Attribute should not be None!")
        self.assertEqual("family", att.name, msg="attribute name differs")

        name = "steel"
        att = data.attribute_by_name(name)
        self.assertIsNotNone(att, msg="Attribute should not be None!")
        self.assertEqual(name, att.name, msg="attribute name differs")
        self.assertEqual(2, att.index, msg="attribute index differs")

        data.delete_attribute(2)
        self.assertEqual(38, data.num_attributes, msg="num_attributes differs")
        name = "steel"
        att = data.attribute_by_name(name)
        self.assertIsNone(att, msg="Attribute should be None!")

        data.delete(3)
        self.assertEqual(897, data.num_instances, msg="num_instances differs")

        data.class_is_last()
        data.no_class()
        self.assertFalse(data.has_class(), msg="Should not have class set!")

        # changing rows
        data1 = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data1, msg="Failed to load data!")
        data2 = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data2, msg="Failed to load data!")

        inst1 = data1.get_instance(0)
        inst2 = data2.get_instance(0)
        self.assertEqual(inst1.values.tolist(), inst2.values.tolist(), msg="values differ")

        data1.add_instance(inst2)
        self.assertEqual(899, data1.num_instances, msg="num_instances differs (add)")

        inst2 = data2.get_instance(2)
        data1.add_instance(inst2, index=10)
        inst1 = data1.get_instance(10)
        self.assertEqual(900, data1.num_instances, msg="num_instances differs (insert)")
        self.assertEqual(inst1.values.tolist(), inst2.values.tolist(), msg="values differ (insert)")

        inst2 = data2.get_instance(1)
        data1.set_instance(0, inst2)
        inst1 = data1.get_instance(0)
        self.assertEqual(inst1.values.tolist(), inst2.values.tolist(), msg="values differ (set)")

        # create instances
        atts = []
        atts.append(dataset.Attribute.create_numeric("num"))
        atts.append(dataset.Attribute.create_nominal("nom", ["yes", "no"]))
        atts.append(dataset.Attribute.create_string("str"))
        atts.append(dataset.Attribute.create_date("dat", "yyyy-MM-dd"))
        data = dataset.Instances.create_instances("created", atts, 3)
        # 1. row
        values = []
        values.append(1.1)
        values.append(data.attribute(1).index_of("no"))
        values.append(data.attribute(2).add_string_value("blah de blah"))
        values.append(data.attribute(3).parse_date("2015-10-12"))
        inst = dataset.Instance.create_instance(values)
        data.add_instance(inst)
        # 2. row
        values = []
        values.append(1.2)
        values.append(data.attribute(1).index_of("yes"))
        values.append(data.attribute(2).add_string_value("pi day!"))
        values.append(data.attribute(3).parse_date("2001-12-31"))
        inst = dataset.Instance.create_instance(values)
        data.add_instance(inst)
        # 3. row
        values = []
        values.append(1.3)
        values.append(data.attribute(1).index_of("no"))
        values.append(data.attribute(2).add_string_value("hello world"))
        values.append(data.attribute(3).parse_date("2011-02-03"))
        inst = dataset.Instance.create_instance(values)
        data.add_instance(inst)

        self.assertEqual(data.get_instance(0).get_value(0), 1.1, msg="Numeric value differs")
        self.assertEqual(data.get_instance(1).get_value(0), 1.2, msg="Numeric value differs")
        self.assertEqual(data.get_instance(2).get_value(0), 1.3, msg="Numeric value differs")
        self.assertEqual(data.get_instance(0).get_string_value(1), "no", msg="Nominal value differs")
        self.assertEqual(data.get_instance(1).get_string_value(1), "yes", msg="Nominal value differs")
        self.assertEqual(data.get_instance(2).get_string_value(1), "no", msg="Nominal value differs")
        self.assertEqual(data.get_instance(0).get_string_value(2), "blah de blah", msg="String value differs")
        self.assertEqual(data.get_instance(1).get_string_value(2), "pi day!", msg="String value differs")
        self.assertEqual(data.get_instance(2).get_string_value(2), "hello world", msg="String value differs")
        self.assertEqual(data.get_instance(0).get_value(3), data.attribute(3).parse_date("2015-10-12"), msg="Date value differs")
        self.assertEqual(data.get_instance(1).get_value(3), data.attribute(3).parse_date("2001-12-31"), msg="Date value differs")
        self.assertEqual(data.get_instance(2).get_value(3), data.attribute(3).parse_date("2011-02-03"), msg="Date value differs")

        # train/test split
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("iris.arff"))
        self.assertIsNotNone(data, msg="Failed to load data!")
        self.assertFalse(data.has_class(), msg="Should not have class set!")
        data.class_is_last()

        perc = 66.6
        train, test = data.train_test_split(perc)
        self.assertIsNotNone(train, msg="Train is None")
        self.assertIsNotNone(test, msg="Test is None")
        self.assertEqual(data.num_instances, train.num_instances + test.num_instances, msg="Total number of instances differ")
        self.assertEqual(train.num_instances, 100, msg="Number of training instances differ")
        self.assertEqual(test.num_instances, 50, msg="Number of test instances differ")
        try:
            perc = 0.0
            data.train_test_split(perc)
            self.fail(msg="Should not accept split percentage of " + str(perc))
        except Exception as e:
            pass
        try:
            perc = -1.0
            data.train_test_split(perc)
            self.fail(msg="Should not accept split percentage of " + str(perc))
        except Exception as e:
            pass
        try:
            perc = 100.0
            data.train_test_split(perc)
            self.fail(msg="Should not accept split percentage of " + str(perc))
        except Exception as e:
            pass
        try:
            perc = 101.0
            data.train_test_split(perc)
            self.fail(msg="Should not accept split percentage of " + str(perc))
        except Exception as e:
            pass

    def test_create_instances_from_lists(self):
        """
        Tests the create_instances_from_lists method.
        """

        # numeric
        x = [[randint(1, 10) for _ in range(5)] for _ in range(10)]
        y = [randint(0, 1) for _ in range(10)]
        self.assertEqual(len(x), 10)
        self.assertEqual(len(y), 10)
        dataset = create_instances_from_lists(x, name="generated from lists (no y)")
        self.assertEqual(len(dataset), 10)
        dataset = create_instances_from_lists(x, y, name="generated from lists")
        self.assertEqual(len(dataset), 10)

        # mixed
        x = [["TEXT", 1, 1.1], ["XXX", 2, 2.2]]
        y = ["A", "B"]
        self.assertEqual(len(x), 2)
        self.assertEqual(len(y), 2)
        dataset = create_instances_from_lists(x, name="generated from mixed lists (no y)")
        self.assertEqual(len(dataset), 2)
        dataset = create_instances_from_lists(x, y, name="generated from mixed lists")
        self.assertEqual(len(dataset), 2)

    def test_create_instances_from_matrices(self):
        """
        Tests the create_instances_from_matrices method.
        """

        # numeric
        x = np.random.randn(10, 5)
        y = np.random.randn(10)
        self.assertEqual(len(x), 10)
        self.assertEqual(len(y), 10)
        dataset = create_instances_from_lists(x, name="generated from lists (no y)")
        self.assertEqual(len(dataset), 10)
        dataset = create_instances_from_lists(x, y, name="generated from lists")
        self.assertEqual(len(dataset), 10)

        # mixed
        x = np.array([("TEXT", 1, 1.1), ("XXX", 2, 2.2)], dtype='S20, i4, f8')
        y = np.array(["A", "B"], dtype='S20')
        self.assertEqual(len(x), 2)
        self.assertEqual(len(y), 2)
        dataset = create_instances_from_matrices(x, name="generated from mixed lists (no y)")
        self.assertEqual(len(dataset), 2)
        dataset = create_instances_from_matrices(x, y, name="generated from mixed lists")
        self.assertEqual(len(dataset), 2)


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestDataset)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
