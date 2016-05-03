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

# classifiers.py
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
from weka.core.classes import Random
import weka.core.converters as converters
import weka.classifiers as classifiers
import weka.filters as filters
import weka.plot.classifiers as plot
import wekatests.tests.weka_test as weka_test


class TestClassifiers(weka_test.WekaTest):

    def test_generate_thresholdcurve_data(self):
        """
        Tests the generate_thresholdcurve_data method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("diabetes.arff"))
        data.class_is_last()

        remove = filters.Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1-3"])
        cls = classifiers.Classifier(classname="weka.classifiers.bayes.NaiveBayes")
        fc = classifiers.FilteredClassifier()
        fc.filter = remove
        fc.classifier = cls

        evl = classifiers.Evaluation(data)
        evl.crossvalidate_model(cls, data, 10, Random(1))
        data = plot.generate_thresholdcurve_data(evl, 0)
        self.assertEqual(13, data.num_attributes, msg="number of attributes differs")
        self.assertEqual(769, data.num_instances, msg="number of rows differs")
        attname = "True Positives"
        self.assertIsNotNone(data.attribute_by_name(attname), msg="Failed to locate attribute: " + attname)
        attname = "False Positive Rate"
        self.assertIsNotNone(data.attribute_by_name(attname), msg="Failed to locate attribute: " + attname)
        attname = "Lift"
        self.assertIsNotNone(data.attribute_by_name(attname), msg="Failed to locate attribute: " + attname)

    def test_get_auc(self):
        """
        Tests the get_auc method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("diabetes.arff"))
        data.class_is_last()

        remove = filters.Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1-3"])
        cls = classifiers.Classifier(classname="weka.classifiers.bayes.NaiveBayes")
        fc = classifiers.FilteredClassifier()
        fc.filter = remove
        fc.classifier = cls

        evl = classifiers.Evaluation(data)
        evl.crossvalidate_model(cls, data, 10, Random(1))
        data = plot.generate_thresholdcurve_data(evl, 0)
        area = plot.get_auc(data)
        self.assertAlmostEqual(0.819, area, places=3, msg="AUC differs")

    def test_get_prc(self):
        """
        Tests the get_prc method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("diabetes.arff"))
        data.class_is_last()

        remove = filters.Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1-3"])
        cls = classifiers.Classifier(classname="weka.classifiers.bayes.NaiveBayes")
        fc = classifiers.FilteredClassifier()
        fc.filter = remove
        fc.classifier = cls

        evl = classifiers.Evaluation(data)
        evl.crossvalidate_model(cls, data, 10, Random(1))
        data = plot.generate_thresholdcurve_data(evl, 0)
        area = plot.get_prc(data)
        self.assertAlmostEqual(0.892, area, places=3, msg="PRC differs")

    def test_plot_classifier_errors(self):
        """
        Tests the plot_classifier_errors method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        bolts_data = loader.load_file(self.datafile("bolts.arff"))
        self.assertIsNotNone(bolts_data)
        bolts_data.class_is_last()

        classifier = classifiers.Classifier(classname="weka.classifiers.functions.LinearRegression", options=["-S", "1", "-C"])
        evaluation = classifiers.Evaluation(bolts_data)
        evaluation.crossvalidate_model(classifier, bolts_data, 10, Random(42))
        plot.plot_classifier_errors(evaluation.predictions, wait=False)

    def test_plot_roc(self):
        """
        Tests the plot_roc method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("diabetes.arff"))
        data.class_is_last()

        remove = filters.Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1-3"])
        cls = classifiers.Classifier(classname="weka.classifiers.bayes.NaiveBayes")
        fc = classifiers.FilteredClassifier()
        fc.filter = remove
        fc.classifier = cls

        evl = classifiers.Evaluation(data)
        evl.crossvalidate_model(cls, data, 10, Random(1))
        plot.plot_roc(evl, class_index=[0, 1], wait=False)

    def test_plot_prc(self):
        """
        Tests the plot_prc method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("diabetes.arff"))
        data.class_is_last()

        remove = filters.Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1-3"])
        cls = classifiers.Classifier(classname="weka.classifiers.bayes.NaiveBayes")
        fc = classifiers.FilteredClassifier()
        fc.filter = remove
        fc.classifier = cls

        evl = classifiers.Evaluation(data)
        evl.crossvalidate_model(cls, data, 10, Random(1))
        plot.plot_prc(evl, class_index=[0, 1], wait=False)

    def test_learning_curve(self):
        """
        Tests the learning_curve method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("diabetes.arff"))
        data.class_is_last()

        cls = [
            classifiers.Classifier(classname="weka.classifiers.trees.J48"),
            classifiers.Classifier(classname="weka.classifiers.bayes.NaiveBayesUpdateable")]
        plot.plot_learning_curve(cls, data, wait=False)
        plot.plot_learning_curve(cls, data, increments=0.1, wait=False)


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestClassifiers)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
