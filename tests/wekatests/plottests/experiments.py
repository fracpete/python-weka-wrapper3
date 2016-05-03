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

# experiments.py
# Copyright (C) 2015-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.converters as converters
import weka.classifiers as classifiers
import weka.experiments as experiments
import weka.plot.experiments as plot
import wekatests.tests.weka_test as weka_test


class TestExperiments(weka_test.WekaTest):

    def test_plot_experiment(self):
        """
        Tests the plot_experiment method.
        """
        datasets = [self.datafile("bolts.arff"), self.datafile("bodyfat.arff"), self.datafile("autoPrice.arff")]
        cls = [
            classifiers.Classifier("weka.classifiers.trees.REPTree"),
            classifiers.Classifier("weka.classifiers.functions.LinearRegression"),
            classifiers.Classifier("weka.classifiers.functions.SMOreg"),
        ]
        outfile = self.tempfile("results-rs.arff")
        exp = experiments.SimpleRandomSplitExperiment(
            classification=False,
            runs=10,
            percentage=66.6,
            preserve_order=False,
            datasets=datasets,
            classifiers=cls,
            result=outfile)
        exp.setup()
        exp.run()

        # evaluate
        loader = converters.loader_for_file(outfile)
        data = loader.load_file(outfile)
        matrix = experiments.ResultMatrix("weka.experiment.ResultMatrixPlainText")
        tester = experiments.Tester("weka.experiment.PairedCorrectedTTester")
        tester.resultmatrix = matrix
        comparison_col = data.attribute_by_name("Correlation_coefficient").index
        tester.instances = data
        tester.header(comparison_col)
        tester.multi_resultset_full(0, comparison_col)

        # plot
        plot.plot_experiment(matrix, title="Random split (w/ StdDev)", measure="Correlation coefficient", show_stdev=True, wait=False)
        plot.plot_experiment(matrix, title="Random split", measure="Correlation coefficient", wait=False)


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestExperiments)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
