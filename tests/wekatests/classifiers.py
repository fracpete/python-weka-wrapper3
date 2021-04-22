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
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.classes as classes
import weka.core.converters as converters
import weka.classifiers as classifiers
import weka.filters as filters
import wekatests.tests.weka_test as weka_test
import weka.attribute_selection as attsel
from weka.core.packages import install_missing_package

class TestClassifiers(weka_test.WekaTest):

    def test_instantiate_classifier(self):
        """
        Tests the instantiation of several classifier classes.
        """
        cname = "weka.classifiers.trees.J48"
        options = None
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, cls.classname, msg="Classnames differ!")

        cname = "weka.classifiers.trees.J48"
        options = ["-C", "0.3"]
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, cls.classname, msg="Classnames differ!")

        cname = "weka.classifiers.meta.FilteredClassifier"
        options = ["-W", "weka.classifiers.trees.J48", "--", "-C", "0.3"]
        cls = classifiers.SingleClassifierEnhancer(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, cls.classname, msg="Classnames differ!")
        fname = "weka.filters.unsupervised.attribute.Remove"
        flter = filters.Filter(classname=fname, options=["-R", "last"])
        cls.filter = flter
        self.assertEqual(fname, cls.filter.classname, msg="Classnames differ!")

        cls = classifiers.FilteredClassifier()
        self.assertIsNotNone(cls, msg="Failed to instantiate FilteredClassifier!")
        self.assertEqual("weka.classifiers.meta.FilteredClassifier", cls.classname, msg="Classnames differ!")

        cname = "weka.classifiers.functions.SMO"
        cls = classifiers.KernelClassifier(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate KernelClassifier: " + cname)
        self.assertEqual(cname, cls.classname, msg="Classnames differ!")
        kname = "weka.classifiers.functions.supportVector.RBFKernel"
        kernel = classifiers.Kernel(classname=kname)
        self.assertIsNotNone(kernel, msg="Failed to instantiate Kernel: " + kname)
        cls.kernel = kernel
        self.assertEqual(kname, cls.kernel.classname, msg="Kernel classnames differ!")

        cname = "weka.classifiers.meta.Vote"
        cls = classifiers.MultipleClassifiersCombiner(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate MultipleClassifiersCombiner: " + cname)
        self.assertEqual(cname, cls.classname, msg="Classnames differ!")

    def test_capabilities(self):
        """
        Tests the capabilities.
        """
        cname = "weka.classifiers.trees.J48"
        options = None
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, cls.classname, msg="Classnames differ!")

        caps = cls.capabilities
        self.assertIsNotNone(caps, msg="Capabilities are None!")

    def test_build_classifier(self):
        """
        Tests the build_classifier method.
        """
        # 1. nominal
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.classifiers.trees.J48"
        options = ["-C", "0.3"]
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))

        cls.build_classifier(data)

        # 2. numeric
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("bolts.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.classifiers.functions.LinearRegression"
        options = ["-R", "0.1"]
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))

        cls.build_classifier(data)

    def test_distribution_for_instance(self):
        """
        Tests the distribution_for_instance method.
        """
        # 1. nominal
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.classifiers.trees.J48"
        options = ["-C", "0.3"]
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))

        cls.build_classifier(data)
        for i in range(10):
            dist = cls.distribution_for_instance(data.get_instance(i))
            self.assertIsNotNone(dist)
            self.assertEqual(6, len(dist), msg="Number of classes in prediction differ!")

        # 2. numeric
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("bolts.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.classifiers.functions.LinearRegression"
        options = ["-R", "0.1"]
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))

        cls.build_classifier(data)
        for i in range(10):
            dist = cls.distribution_for_instance(data.get_instance(i))
            self.assertIsNotNone(dist)
            self.assertEqual(1, len(dist), msg="Number of classes in prediction should be one for numeric classifier!")

    def test_batchpredictor(self):
        """
        Tests the batch predictor methods.
        """

        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.classifiers.trees.J48"
        options = []
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))

        # batch predictor?
        self.assertTrue(cls.is_batchpredictor, msg="not a batch predictor: " + cname + "/" + str(options))

        # more efficient implementation?
        cls.has_efficient_batch_prediction()

        # batch size
        self.assertIsNotNone(cls.batch_size, msg="batch size is not initialized")

        # distributions_for_instances
        cls.build_classifier(data)
        dists = cls.distributions_for_instances(data)
        self.assertIsNotNone(dists, msg="no distributions generated")
        self.assertEqual(len(dists), len(data), msg="number of predictions differ")
        self.assertEqual(len(dists[0]), data.class_attribute.num_values, msg="size of distribution array does not match number of classes")

    def test_classify_instance(self):
        """
        Tests the classify_instance method.
        """
        # 1. nominal
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.classifiers.trees.J48"
        options = ["-C", "0.3"]
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))

        cls.build_classifier(data)
        preds = []
        for i in range(10,20):
            pred = cls.classify_instance(data.get_instance(i))
            self.assertIsNotNone(pred)
            preds.append(pred)
        self.assertEqual(
            [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 5.0, 5.0, 2.0, 2.0],
            preds, msg="Classifications differ")

        # 2. numeric
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("bolts.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.classifiers.functions.LinearRegression"
        options = ["-R", "0.1"]
        cls = classifiers.Classifier(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))

        cls.build_classifier(data)
        preds = []
        for i in range(10):
            pred = cls.classify_instance(data.get_instance(i))
            self.assertIsNotNone(pred)
            preds.append(pred)
        expected = [24.313, 33.359, 28.569, 26.365, 32.680, 29.149, 26.998, 22.971, 13.160, 7.394]
        for i in range(len(preds)):
            self.assertAlmostEqual(expected[i], preds[i], places=3, msg="Classifications differ")

    def test_costmatrix(self):
        """
        Tests the CostMatrix class.
        """
        cmatrix = classifiers.CostMatrix(num_classes=3)
        self.assertEqual(3, cmatrix.num_columns, msg="# of columns differ")
        self.assertEqual(3, cmatrix.num_rows, msg="# of rows differ")

        self.assertEqual(0, cmatrix.get_element(1, 1), msg="cell should be initialized with 0")
        cmatrix.set_element(1, 1, 0.1)
        self.assertEqual(0.1, cmatrix.get_element(1, 1), msg="cell value differs")

        matrixstr = "[1.0 2.0; 3.0 4.0]"
        cmatrix = classifiers.CostMatrix.parse_matlab(matrixstr)
        self.assertEqual(matrixstr, cmatrix.to_matlab(), msg="Matrix strings differ")

    def test_evaluation(self):
        """
        Tests the Evaluation class.
        """
        # 1. nominal
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.classifiers.trees.J48"
        cls = classifiers.Classifier(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname)

        evl = classifiers.Evaluation(data)
        self.assertIsNotNone(evl, msg="Failed to instantiate Evaluation")
        self.assertIsNone(evl.header.equal_headers(data))
        self.assertEqual([9, 100, 685, 1, 68, 41], evl.class_priors.tolist())

        # cross-validate
        evl.crossvalidate_model(cls, data, 10, classes.Random(1))
        self.assertEqual([[5.0, 0.0, 3.0, 0.0, 0.0, 0.0], [0.0, 99.0, 0.0, 0.0, 0.0, 0.0], [0.0, 2.0, 680.0, 0.0, 0.0, 2.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 67.0, 0.0], [0.0, 0.0, 7.0, 0.0, 0.0, 33.0]], evl.confusion_matrix.tolist(), msg="confusion matrix differs")
        self.assertAlmostEqual(0.749, evl.area_under_prc(0), places=3, msg="area_under_prc(0) differs")
        self.assertAlmostEqual(0.931, evl.area_under_roc(0), places=3, msg="area_under_roc(0) differs")
        self.assertAlmostEqual(0, evl.avg_cost, places=3, msg="avg_cost differs")
        self.assertEqual(884, evl.correct, msg="correct differs")
        self.assertAlmostEqual(98.775, evl.coverage_of_test_cases_by_predicted_regions, places=3, msg="coverage_of_test_cases_by_predicted_regions differs")
        self.assertAlmostEqual(0.016, evl.error_rate, places=3, msg="error_rate differs")
        self.assertAlmostEqual(0.769, evl.f_measure(0), places=3, msg="f_measure(0) differs")
        self.assertAlmostEqual(0.375, evl.false_negative_rate(0), places=3, msg="false_negative_rate(0) differs")
        self.assertAlmostEqual(0.0, evl.false_positive_rate(0), places=3, msg="false_positive_rate(0) differs")
        self.assertEqual(14, evl.incorrect, msg="incorrect differs")
        self.assertAlmostEqual(0.961, evl.kappa, places=3, msg="kappa differs")
        self.assertAlmostEqual(1017.196, evl.kb_information, places=3, msg="kb_information differs")
        self.assertAlmostEqual(1.133, evl.kb_mean_information, places=3, msg="kb_mean_information differs")
        self.assertAlmostEqual(95.017, evl.kb_relative_information, places=3, msg="kb_relative_information differs")
        self.assertAlmostEqual(0.789, evl.matthews_correlation_coefficient(0), places=3, msg="matthews_correlation_coefficient(0) differs")
        self.assertAlmostEqual(0.006, evl.mean_absolute_error, places=3, msg="mean_absolute_error differs")
        self.assertAlmostEqual(0.134, evl.mean_prior_absolute_error, places=3, msg="mean_prior_absolute_error differs")
        self.assertAlmostEqual(3.0, evl.num_false_negatives(0), places=3, msg="num_false_negatives(0) differs")
        self.assertAlmostEqual(0.0, evl.num_false_positives(0), places=3, msg="num_false_positives(0) differs")
        self.assertAlmostEqual(898.0, evl.num_instances, places=3, msg="num_instances differs")
        self.assertAlmostEqual(890.0, evl.num_true_negatives(0), places=3, msg="num_true_negatives(0) differs")
        self.assertAlmostEqual(5.0, evl.num_true_positives(0), places=3, msg="num_true_positives(0) differs")
        self.assertAlmostEqual(98.44, evl.percent_correct, places=2, msg="percent_correct differs")
        self.assertAlmostEqual(1.56, evl.percent_incorrect, places=2, msg="percent_incorrect differs")
        self.assertAlmostEqual(0, evl.percent_unclassified, places=2, msg="percent_unclassified differs")
        self.assertAlmostEqual(1.0, evl.precision(0), places=3, msg="precision(0) differs")
        self.assertAlmostEqual(0.625, evl.recall(0), places=3, msg="recall(0) differs")
        self.assertAlmostEqual(4.187, evl.relative_absolute_error, places=3, msg="relative_absolute_error differs")
        self.assertAlmostEqual(0.258, evl.root_mean_prior_squared_error, places=3, msg="root_mean_prior_squared_error differs")
        self.assertAlmostEqual(0.067, evl.root_mean_squared_error, places=3, msg="root_mean_squared_error differs")
        self.assertAlmostEqual(25.912, evl.root_relative_squared_error, places=3, msg="root_relative_squared_error differs")
        self.assertAlmostEqual(-75.044, evl.sf_entropy_gain, places=3, msg="sf_entropy_gain differs")
        self.assertAlmostEqual(-0.084, evl.sf_mean_entropy_gain, places=3, msg="sf_mean_entropy_gain differs")
        self.assertAlmostEqual(1.192, evl.sf_mean_prior_entropy, places=3, msg="sf_mean_prior_entropy differs")
        self.assertAlmostEqual(1.276, evl.sf_mean_scheme_entropy, places=3, msg="sf_mean_scheme_entropy differs")
        self.assertAlmostEqual(16.722, evl.size_of_predicted_regions, places=3, msg="size_of_predicted_regions differs")
        self.assertEqual(0, evl.unclassified, msg="unclassified differs")
        self.assertAlmostEqual(0.0, evl.total_cost, places=3, msg="total_cost differs")
        self.assertAlmostEqual(0.926, evl.unweighted_macro_f_measure, places=3, msg="unweighted_macro_f_measure differs")
        self.assertAlmostEqual(0.984, evl.unweighted_micro_f_measure, places=3, msg="unweighted_micro_f_measure differs")
        self.assertAlmostEqual(0.992, evl.weighted_area_under_prc, places=3, msg="weighted_area_under_prc differs")
        self.assertAlmostEqual(0.995, evl.weighted_area_under_roc, places=3, msg="weighted_area_under_roc differs")
        self.assertAlmostEqual(0.984, evl.weighted_f_measure, places=3, msg="weighted_f_measure differs")
        self.assertAlmostEqual(0.016, evl.weighted_false_negative_rate, places=3, msg="weighted_false_negative_rate differs")
        self.assertAlmostEqual(0.036, evl.weighted_false_positive_rate, places=3, msg="weighted_false_positive_rate differs")
        self.assertAlmostEqual(0.959, evl.weighted_matthews_correlation, places=3, msg="weighted_matthews_correlation differs")
        self.assertAlmostEqual(0.984, evl.weighted_precision, places=3, msg="weighted_precision differs")
        self.assertAlmostEqual(0.984, evl.weighted_recall, places=3, msg="weighted_recall differs")
        self.assertAlmostEqual(0.964, evl.weighted_true_negative_rate, places=3, msg="weighted_true_negative_rate differs")
        self.assertAlmostEqual(0.984, evl.weighted_true_positive_rate, places=3, msg="weighted_true_positive_rate differs")
        self.assertIsNotNone(evl.predictions, msg="Should have had predictions")
        self.assertEqual(data.num_instances, len(evl.predictions), msg="Number of predictions differ from training set size")

        # train/test
        evl = classifiers.Evaluation(data)
        self.assertIsNotNone(evl, msg="Failed to instantiate Evaluation")
        cname = "weka.classifiers.trees.J48"
        cls = classifiers.Classifier(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname)
        cls.build_classifier(data)
        evl.test_model(cls, data)
        self.assertAlmostEqual(99.777, evl.percent_correct, places=3, msg="percent_correct differs")

        # predictions: no
        cname = "weka.classifiers.trees.J48"
        cls = classifiers.Classifier(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname)
        evl = classifiers.Evaluation(data)
        evl.discard_predictions = True
        self.assertIsNotNone(evl, msg="Failed to instantiate Evaluation")
        evl.crossvalidate_model(cls, data, 10, classes.Random(1))
        self.assertIsNone(evl.predictions, msg="Should have had no predictions")

        # output
        cname = "weka.classifiers.trees.J48"
        cls = classifiers.Classifier(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname)
        evl = classifiers.Evaluation(data)
        cname = "weka.classifiers.evaluation.output.prediction.PlainText"
        pout = classifiers.PredictionOutput(classname=cname)
        self.assertEqual(cname, pout.classname, msg="Output classnames differ!")
        self.assertIsNotNone(evl, msg="Failed to instantiate Evaluation")
        evl.crossvalidate_model(cls, data, 10, classes.Random(1), output=pout)
        self.assertGreater(len(str(pout)), 0, msg="Should have generated output")

        # 2. numeric
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("bolts.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.classifiers.functions.LinearRegression"
        cls = classifiers.Classifier(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname )

        evl = classifiers.Evaluation(data)
        self.assertIsNotNone(evl, msg="Failed to instantiate Evaluation")
        self.assertIsNone(evl.header.equal_headers(data))

        # cross-validate
        evl.crossvalidate_model(cls, data, 10, classes.Random(1))
        self.assertAlmostEqual(0.919, evl.correlation_coefficient, places=3, msg="correlation_coefficient differs")
        self.assertAlmostEqual(10.697, evl.error_rate, places=3, msg="error_rate differs")

    def test_gridsearch(self):
        """
        Tests the GridSearch class.
        """
        # make sure the package is installed
        install_missing_package("gridSearch", stop_jvm_and_exit=True)

        gs = classifiers.GridSearch()

        self.assertEqual({"property": "C", "expression": "pow(BASE,I)", "min": -3.0, "max": 3.0, "step": 1.0, "base": 10.0}, gs.x, msg="x of grid differs")
        x = gs.x
        x["min"] = -1.0
        x["max"] = 2.0
        gs.x = x
        self.assertEqual({"property": "C", "expression": "pow(BASE,I)", "min": -1.0, "max": 2.0, "step": 1.0, "base": 10.0}, gs.x, msg="x of grid differs")

        self.assertEqual({"property": "kernel.gamma", "expression": "pow(BASE,I)", "min": -3.0, "max": 3.0, "step": 1.0, "base": 10.0}, gs.y, msg="y of grid differs")
        y = gs.y
        y["min"] = -1.0
        y["max"] = 2.0
        gs.y = y
        self.assertEqual({"property": "kernel.gamma", "expression": "pow(BASE,I)", "min": -1.0, "max": 2.0, "step": 1.0, "base": 10.0}, gs.y, msg="y of grid differs")

        cls = classifiers.Classifier(classname="weka.classifiers.functions.LinearRegression")
        gs.classifier = cls
        gs.evaluation = gs.tags_evaluation.find("RMSE")
        self.assertEqual("RMSE", str(gs.evaluation), "evaluation differs: " + str(gs.evaluation))

        gs.evaluation = "ACC"
        self.assertEqual("ACC", str(gs.evaluation), "evaluation differs: " + str(gs.evaluation))
        cls = classifiers.Classifier(classname="weka.classifiers.trees.J48")
        gs.classifier = cls

    def test_multisearch(self):
        """
        Tests the MultiSearch class.
        NB: multisearch-weka-package must be installed (https://github.com/fracpete/multisearch-weka-package).
        """
        # make sure the package is installed
        install_missing_package("multisearch", stop_jvm_and_exit=True)

        ms = classifiers.MultiSearch()

        mparam = classes.MathParameter()
        mparam.prop = "classifier.kernel.gamma"
        mparam.minimum = -3.0
        mparam.maximum = 3.0
        mparam.step = 1.0
        mparam.base = 10.0
        mparam.expression = "pow(BASE,I)"
        lparam = classes.ListParameter()
        lparam.prop = "classifier.C"
        lparam.values = ["-2.0", "-1.0", "0.0", "1.0", "2.0"]
        ms.parameters = [mparam, lparam]
        self.assertEqual(str([mparam, lparam]), str(ms.parameters), msg="parameters differ")

        cls = classifiers.Classifier(
            classname="weka.classifiers.functions.SMOreg",
            options=["-K", "weka.classifiers.functions.supportVector.RBFKernel"])
        ms.classifier = cls
        self.assertEqual(cls.to_commandline(), ms.classifier.to_commandline(), msg="classifiers differ")

        cls = classifiers.Classifier(classname="weka.classifiers.functions.LinearRegression")
        ms.classifier = cls
        ms.evaluation = ms.tags_evaluation.find("RMSE")
        self.assertEqual("RMSE", str(ms.evaluation), "evaluation differs: " + str(ms.evaluation))

        ms.evaluation = "ACC"
        self.assertEqual("ACC", str(ms.evaluation), "evaluation differs: " + str(ms.evaluation))
        cls = classifiers.Classifier(classname="weka.classifiers.trees.J48")
        ms.classifier = cls

    def test_attributeselectedclassifier(self):
        """
        Tests the AttributeSelectedClassifier class.
        """
        asc = classifiers.AttributeSelectedClassifier()
        asc.evaluator = attsel.ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval", options=["-P", "1", "-E", "1"])
        asc.search = attsel.ASSearch(classname="weka.attributeSelection.GreedyStepwise", options=["-B", "-T", "-1.7E308", "-N", "-1", "-num-slots", "1"])
        self.assertEqual("weka.attributeSelection.CfsSubsetEval -P 1 -E 1", asc.evaluator.to_commandline(), msg="evaluator command-lines differs")
        self.assertEqual("weka.attributeSelection.GreedyStepwise -B -T -1.7E308 -N -1 -num-slots 1", asc.search.to_commandline(), msg="search command-lines differs")


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestClassifiers)


if __name__ == '__main__':
    jvm.start(packages=True)   # necessary for multisearch
    unittest.TextTestRunner().run(suite())
    jvm.stop()
