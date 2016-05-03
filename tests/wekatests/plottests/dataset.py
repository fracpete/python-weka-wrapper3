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
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.converters as converters
import weka.core.dataset as dataset
import weka.plot.dataset as plot
import wekatests.tests.weka_test as weka_test


class TestDataset(weka_test.WekaTest):

    def test_scatter_plot(self):
        """
        Tests the scatter_plot method.
        """
        loader = converters.Loader("weka.core.converters.ArffLoader")
        iris_data = loader.load_file(self.datafile("iris.arff"))
        iris_data.class_is_last()
        plot.scatter_plot(
            iris_data, iris_data.attribute_by_name("petalwidth").index,
            iris_data.attribute_by_name("petallength").index,
            percent=50,
            wait=False)

    def test_matrix_plot(self):
        """
        Tests the matrix_plot method.
        """
        loader = converters.Loader("weka.core.converters.ArffLoader")
        iris_data = loader.load_file(self.datafile("iris.arff"))
        iris_data.class_is_last()
        plot.matrix_plot(iris_data, percent=50, title="Matrix plot iris", wait=False)


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
