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

# datagenerators.py
# Copyright (C) 2014 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.datagenerators as datagenerators
import wekatests.tests.weka_test as weka_test


class TestDataGenerators(weka_test.WekaTest):

    def test_batch(self):
        """
        Tests the batch generation.
        """
        generator = datagenerators.DataGenerator(
            classname="weka.datagenerators.classifiers.classification.Agrawal", options=["-n", "10", "-r", "agrawal"])
        generator.dataset_format = generator.define_data_format()
        self.assertEqual(10, generator.dataset_format.num_attributes, msg="Number of attributes differs")
        data = generator.generate_examples()
        self.assertEqual(10, data.num_instances, msg="Number of rows differs")

    def test_incremental(self):
        """
        Tests the incremental generation.
        """
        generator = datagenerators.DataGenerator(
            classname="weka.datagenerators.classifiers.classification.Agrawal", options=["-n", "10", "-r", "agrawal"])
        generator.dataset_format = generator.define_data_format()
        self.assertEqual(10, generator.dataset_format.num_attributes, msg="Number of attributes differs")
        count = 0
        for i in range(generator.num_examples_act):
            count += 1
        self.assertEqual(10, count, msg="Number of rows differs")


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestDataGenerators)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
