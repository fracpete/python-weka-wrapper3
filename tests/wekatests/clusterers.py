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
import weka.core.dataset as dataset
import weka.core.classes as classes
import weka.clusterers as clusterers
import weka.filters as filters
import wekatests.tests.weka_test as weka_test


class TestClusterers(weka_test.WekaTest):

    def test_instantiate_clusterer(self):
        """
        Tests the instantion of Clusterer objects.
        """
        cname = "weka.clusterers.SimpleKMeans"
        cls = clusterers.Clusterer(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        self.assertEqual(cname, cls.classname, msg="Classnames differ!")

        cls = clusterers.FilteredClusterer()
        self.assertIsNotNone(cls, msg="Failed to instantiate filtered clusterer!")
        self.assertEqual("weka.clusterers.FilteredClusterer", cls.classname, msg="Classnames differ!")
        cname = "weka.filters.unsupervised.attribute.Remove"
        flter = filters.Filter(classname=cname)
        self.assertEqual(cname, flter.classname, msg="Filter classnames differ!")
        cls.filter = flter
        self.assertEqual(cname, cls.filter.classname, msg="Filter classnames differ!")
        cname = "weka.clusterers.EM"
        cls.clusterer = clusterers.Clusterer(classname=cname)
        self.assertEqual(cname, cls.clusterer.classname, msg="Base clusterer classnames differ!")

    def test_make_copy(self):
        """
        Tests the make_copy class method of the Clusterer class.
        """
        cname = "weka.clusterers.SimpleKMeans"
        cls = clusterers.Clusterer(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        self.assertEqual(cname, cls.classname, msg="Classnames differ!")
        cls2 = clusterers.Clusterer.make_copy(cls)
        self.assertIsNotNone(cls2, msg="Failed to instantiate clusterer!")
        self.assertEqual(cname, cls2.classname, msg="Classnames differ!")

    def test_capabilities(self):
        """
        Tests the capabilities.
        """
        cname = "weka.clusterers.SimpleKMeans"
        cls = clusterers.Clusterer(classname=cname)
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        self.assertEqual(cname, cls.classname, "Classnames differ!")

        caps = cls.capabilities
        self.assertIsNotNone(caps, msg="Capabilities are None!")

    def test_build_clusterer(self):
        """
        Tests the build_clusterer class.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.delete_last_attribute()

        # batch
        cls = clusterers.Clusterer(classname="weka.clusterers.SimpleKMeans")
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        cls.build_clusterer(data)
        self.assertIsNotNone(str(cls), msg="Failed to obtain string representation of model")

        # incremental
        cls = clusterers.Clusterer(classname="weka.clusterers.Cobweb")
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        cls.build_clusterer(dataset.Instances.template_instances(data))
        for inst in data:
            cls.update_clusterer(inst)
        cls.update_finished()
        self.assertIsNotNone(str(cls), msg="Failed to obtain string representation of model")

    def test_cluster_instance(self):
        """
        Tests the cluster_instance class.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.delete_last_attribute()

        cls = clusterers.Clusterer(classname="weka.clusterers.SimpleKMeans")
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        cls.build_clusterer(data)

        preds = []
        for i in range(10):
            cluster = cls.cluster_instance(data.get_instance(i))
            self.assertIsNotNone(cluster, msg="Failed to cluster instance")
            preds.append(cluster)
        self.assertEqual([1, 0, 0, 1, 1, 1, 0, 0, 0, 0], preds, msg="Clusters differ")

    def test_distribution_for_instance(self):
        """
        Tests the distribution_for_instance method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.delete_last_attribute()

        cls = clusterers.Clusterer(classname="weka.clusterers.SimpleKMeans")
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        cls.build_clusterer(data)

        preds = []
        for i in range(10):
            dist = cls.distribution_for_instance(data.get_instance(i))
            self.assertIsNotNone(dist, msg="Failed to obtain cluster membership for instance")
            self.assertEqual(2, len(dist), msg="Number of clusters differs")
            preds.append(dist)
        expected = [[0., 1.], [1., 0.], [1., 0.], [0., 1.], [0., 1.], [0., 1.], [1., 0.], [1., 0.], [1., 0.], [1., 0.]]
        self.assertEqual(len(expected), len(preds), msg="Expected/predicted differ in length - update required!")
        for i in range(len(expected)):
            self.assertEqual(expected[i], preds[i].tolist(), msg="Cluster distributions differ")

    def test_clusterevaluation(self):
        """
        Tests the ClusterEvaluation class.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        data.delete_last_attribute()

        # simple test set
        test = dataset.Instances.copy_instances(data, 0, 10)
        cls = clusterers.Clusterer(classname="weka.clusterers.SimpleKMeans")
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        cls.build_clusterer(data)

        evl = clusterers.ClusterEvaluation()
        self.assertIsNotNone(cls, msg="Failed to instantiate evaluation!")
        evl.set_model(cls)
        evl.test_model(test)
        self.assertGreater(len(evl.cluster_results), 0, msg="No evaluation string!")
        self.assertEqual(0.0, evl.log_likelihood, msg="log_likelihood differs")
        self.assertEqual(2, evl.num_clusters, msg="num_clusters differs")
        self.assertEquals(
            [1., 0., 0., 1., 1., 1., 0., 0., 0., 0.], evl.cluster_assignments.tolist(),
            msg="cluster_assignments differs")

        # cross-validation
        cls = clusterers.Clusterer(classname="weka.clusterers.EM", options=["-I", "3", "-X", "2", "-max", "5"])
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        llh = clusterers.ClusterEvaluation.crossvalidate_model(cls, data, 10, classes.Random(1))
        self.assertAlmostEqual(-34.397, llh, places=3, msg="Failed to cross-validate clusterer!")

    def test_classes_to_clusters(self):
        """
        Tests the classes_to_clusters method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("anneal.arff"))
        self.assertIsNotNone(data)
        #data.class_is_last()

        train = dataset.Instances.copy_instances(data, 0, data.num_instances)
        train.delete_last_attribute()

        cls = clusterers.Clusterer(classname="weka.clusterers.SimpleKMeans")
        self.assertIsNotNone(cls, msg="Failed to instantiate clusterer!")
        cls.build_clusterer(train)

        test = dataset.Instances.copy_instances(data, 0, data.num_instances)
        test.class_is_last()
        evl = clusterers.ClusterEvaluation()
        self.assertIsNotNone(cls, msg="Failed to instantiate evaluation!")
        evl.set_model(cls)
        evl.test_model(test)
        self.assertEqual([2, 4], evl.classes_to_clusters.tolist(), msg="classes to clusters differs")


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
