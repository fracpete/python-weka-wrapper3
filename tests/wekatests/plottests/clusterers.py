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

# clusterers.py
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.converters as converters
import weka.clusterers as clusterers
import weka.plot.clusterers as plot
import wekatests.tests.weka_test as weka_test


class TestClusterers(weka_test.WekaTest):

    def test_plot_cluster_assignments(self):
        """
        Tests the plot_cluster_assignments method.
        """
        loader = converters.Loader("weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("iris.arff"))
        data.delete_last_attribute()

        # build a clusterer and output model
        clusterer = clusterers.Clusterer(classname="weka.clusterers.SimpleKMeans", options=["-N", "3"])
        clusterer.build_clusterer(data)
        evaluation = clusterers.ClusterEvaluation()
        evaluation.set_model(clusterer)
        evaluation.test_model(data)
        plot.plot_cluster_assignments(evaluation, data, inst_no=True, wait=False)


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestClusterers)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
