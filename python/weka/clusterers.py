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
# Copyright (C) 2014-2024 Fracpete (pythonwekawrapper at gmail dot com)

import logging
import os
import sys
import argparse
import traceback
import weka.core.jvm as jvm
import weka.core.typeconv as typeconv
import weka.core.classes as classes
from jpype import JClass
from weka.core.classes import serialization_write, serialization_read_all, serialization_write_all
from weka.core.classes import JavaObject, join_options
from weka.core.classes import OptionHandler
from weka.core.classes import Random
from weka.core.capabilities import Capabilities
from weka.core.dataset import Instances
from weka.core.distances import DistanceFunction
from weka.filters import Filter

# logging setup
logger = logging.getLogger("weka.clusterers")
logger.setLevel(logging.INFO)


class Clusterer(OptionHandler):
    """
    Wrapper class for clusterers.
    """

    def __init__(self, classname="weka.clusterers.SimpleKMeans", jobject=None, options=None):
        """
        Initializes the specified clusterer using either the classname or the supplied JPype object.

        :param classname: the classname of the clusterer
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: the list of commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = Clusterer.new_instance(classname)
        self.is_updateable = self.check_type(jobject, "weka.clusterers.UpdateableClusterer")
        self.is_drawable = self.check_type(jobject, "weka.core.Drawable")
        self.enforce_type(jobject, "weka.clusterers.Clusterer")
        self._header = None
        super(Clusterer, self).__init__(jobject=jobject, options=options)

    def _make_calls(self):
        """
        Method for obtaining method instances for faster access.
        Members must start with "_mc_"
        """
        super(Clusterer, self)._make_calls()
        self._mc_cluster = self.jobject.clusterInstance
        self._mc_distribution = self.jobject.distributionForInstance

    @property
    def capabilities(self):
        """
        Returns the capabilities of the clusterer.

        :return: the capabilities
        :rtype: Capabilities
        """
        return Capabilities(self.jobject.getCapabilities())

    @property
    def header(self):
        """
        Returns the header of the training data.

        :return: the structure of the training data, None if not available
        :rtype: Instances
        """
        return self._header

    def build_clusterer(self, data):
        """
        Builds the clusterer with the data.

        :param data: the data to use for training the clusterer
        :type data: Instances
        """
        self._header = data.copy_structure()
        self.jobject.buildClusterer(data.jobject)

    def update_clusterer(self, inst):
        """
        Updates the clusterer with the instance.

        :param inst: the Instance to update the clusterer with
        :type inst: Instance
        """
        if self.is_updateable:
            self.jobject.updateClusterer(inst.jobject)
        else:
            logger.critical(classes.get_classname(self.jobject) + " is not updateable!")

    def update_finished(self):
        """
        Signals the clusterer that updating with new data has finished.
        """
        if self.is_updateable:
            self.jobject.updateFinished()
        else:
            logger.critical(classes.get_classname(self.jobject) + " is not updateable!")

    def cluster_instance(self, inst):
        """
        Peforms a prediction.

        :param inst: the instance to determine the cluster for
        :type inst: Instance
        :return: the clustering result
        :rtype: float
        """
        return self._mc_cluster(inst.jobject)

    def distribution_for_instance(self, inst):
        """
        Peforms a prediction, returning the cluster distribution.

        :param inst: the Instance to get the cluster distribution for
        :type inst: Instance
        :return: the cluster distribution
        :rtype: np.ndarray
        """
        return typeconv.jdouble_array_to_ndarray(self._mc_distribution(inst.jobject))

    @property
    def number_of_clusters(self):
        """
        Returns the number of clusters found.

        :return: the number fo clusters
        :rtype: int
        """
        return self.jobject.numberOfClusters()

    @property
    def graph_type(self):
        """
        Returns the graph type if classifier implements weka.core.Drawable, otherwise -1.

        :return: the type
        :rtype: int
        """
        if self.is_drawable:
            return self.jobject.graphType()
        else:
            return -1

    @property
    def graph(self):
        """
        Returns the graph if classifier implements weka.core.Drawable, otherwise None.

        :return: the graph or None if not available
        :rtype: str
        """
        if self.is_drawable:
            return self.jobject.graph()
        else:
            return None

    @classmethod
    def make_copy(cls, clusterer):
        """
        Creates a copy of the clusterer.

        :param clusterer: the clustererto copy
        :type clusterer: Clusterer
        :return: the copy of the clusterer
        :rtype: Clusterer
        """
        return Clusterer(jobject=JClass("weka.clusterers.AbstractClusterer").makeCopy(clusterer.jobject))

    @classmethod
    def deserialize(cls, ser_file):
        """
        Deserializes a clusterer from a file.

        :param ser_file: the model file to deserialize
        :type ser_file: str
        :return: model and, if available, the dataset header
        :rtype: tuple
        """

        objs = serialization_read_all(ser_file)
        if len(objs) == 1:
            return Clusterer(jobject=objs[0]), None
        elif len(objs) == 2:
            return Clusterer(jobject=objs[0]), Instances(jobject=objs[1])
        else:
            raise Exception(
                "Excepted one or two objects in the model file (%s), but encountered: %d" % (ser_file, len(objs)))

    def serialize(self, ser_file, header=None):
        """
        Serializes the clusterer to the specified file.

        :param ser_file: the file to save the model to
        :type ser_file: str
        :param header: the (optional) dataset header to store alongside; recommended
        :type header: Instances
        """

        if (header is not None) and header.num_instances > 0:
            header = Instances.template_instances(header)

        if header is not None:
            serialization_write_all(ser_file, [self, header])
        else:
            serialization_write(ser_file, self)


class SingleClustererEnhancer(Clusterer):
    """
    Wrapper class for clusterers that use a single base clusterer.
    """

    def __init__(self, classname=None, jobject=None, options=None):
        """
        Initializes the specified clusterer using either the classname or the supplied JPype object.

        :param classname: the classname of the clusterer
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: the list of commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = Clusterer.new_instance(classname)
        self.enforce_type(jobject, "weka.clusterers.SingleClustererEnhancer")
        super(SingleClustererEnhancer, self).__init__(classname=classname, jobject=jobject, options=options)

    @property
    def clusterer(self):
        """
        Returns the base clusterer.

        :return: the clusterer
        :rtype: Clusterer
        """
        return Clusterer(jobject=self.jobject.getClusterer())

    @clusterer.setter
    def clusterer(self, clusterer):
        """
        Sets the base clusterer.

        :param clusterer: the base clusterer to use
        :type clusterer: Clusterer
        """
        self.jobject.setClusterer(clusterer.jobject)


class FilteredClusterer(SingleClustererEnhancer):
    """
    Wrapper class for the filtered clusterer.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified clusterer using either the classname or the supplied JPype object.

        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: the list of commandline options to use
        :type options: list
        """
        classname = "weka.clusterers.FilteredClusterer"
        if jobject is None:
            jobject = Clusterer.new_instance(classname)
        self.enforce_type(jobject, classname)
        super(FilteredClusterer, self).__init__(classname=classname, jobject=jobject, options=options)

    @property
    def filter(self):
        """
        Returns the filter.

        :return: the filter
        :rtype: weka.filters.Filter
        """
        return Filter(jobject=self.jobject.getFilter())

    @filter.setter
    def filter(self, filtr):
        """
        Sets the filter.

        :param filtr: the filter to use
        :type filtr: weka.filters.Filter
        """
        self.jobject.setFilter(filtr.jobject)


class ClusterEvaluation(JavaObject):
    """
    Evaluation class for clusterers.
    """

    def __init__(self):
        """
        Initializes a ClusterEvaluation object.
        """
        super(ClusterEvaluation, self).__init__(ClusterEvaluation.new_instance("weka.clusterers.ClusterEvaluation"))

    def set_model(self, clusterer):
        """
        Sets the built clusterer to evaluate.

        :param clusterer: the clusterer to evaluate
        :type clusterer: Clusterer
        """
        self.jobject.setClusterer(clusterer.jobject)

    def test_model(self, test):
        """
        Evaluates the currently set clusterer on the test set.

        :param test: the test set to use for evaluating
        :type test: Instances
        """
        self.jobject.evaluateClusterer(test.jobject)

    @property
    def cluster_results(self):
        """
        The cluster results as string.

        :return: the results string
        :rtype: str
        """
        return self.jobject.clusterResultsToString()

    @property
    def cluster_assignments(self):
        """
        Return an array of cluster assignments corresponding to the most recent set of instances clustered.

        :return: the cluster assignments
        :rtype: ndarray
        """
        array = self.jobject.getClusterAssignments()
        if array is None:
            return None
        else:
            return typeconv.jdouble_array_to_ndarray(array)

    @property
    def num_clusters(self):
        """
        Returns the number of clusters.

        :return: the number of clusters
        :rtype: int
        """
        return self.jobject.getNumClusters()

    @property
    def log_likelihood(self):
        """
        Returns the log likelihood.

        :return: the log likelihood
        :rtype: float
        """
        return self.jobject.getLogLikelihood()

    @property
    def classes_to_clusters(self):
        """
        Return the array (ordered by cluster number) of minimum error class to cluster mappings.

        :return: the mappings
        :rtype: ndarray
        """
        array = self.jobject.getClassesToClusters()
        if array is None:
            return None
        else:
            return typeconv.jint_array_to_ndarray(array)

    @classmethod
    def evaluate_clusterer(cls, clusterer, args):
        """
        Evaluates the clusterer with the given options.

        :param clusterer: the clusterer instance to evaluate
        :type clusterer: Clusterer
        :param args: the command-line arguments
        :type args: list
        :return: the evaluation result
        :rtype: str
        """
        return JClass("weka.clusterers.ClusterEvaluation").evaluateClusterer(clusterer.jobject, args)

    @classmethod
    def crossvalidate_model(cls, clusterer, data, num_folds, rnd):
        """
        Cross-validates the clusterer and returns the loglikelihood.

        :param clusterer: the clusterer instance to evaluate
        :type clusterer: Clusterer
        :param data: the data to evaluate on
        :type data: Instances
        :param num_folds: the number of folds
        :type num_folds: int
        :param rnd: the random number generator to use
        :type rnd: Random
        :return: the cross-validated loglikelihood
        :rtype: float
        """
        return JClass("weka.clusterers.ClusterEvaluation").crossValidateModel(
            clusterer.jobject, data.jobject, num_folds, rnd.jobject)


def avg_silhouette_coefficient(clusterer, dist_func, data):
    """
    Computes the average silhouette coefficient for a clusterer.
    Based on Eibe Frank's Groovy code:
    https://weka.8497.n7.nabble.com/Silhouette-Measures-and-Dunn-Index-DI-in-Weka-td44072.html

    :param clusterer: the trained clusterer model to evaluate
    :type clusterer: Clusterer
    :param dist_func: the distance function to use; if Euclidean, make sure that normalization is turned off
    :type dist_func: DistanceFunction
    :return: the average silhouette coefficient
    :param data: the standardized data
    :type data: Instances
    :rtype: float
    """
    # ensure that distance function is initialized with data
    dist_func.instances = data

    cluster_index_of_inst = []
    for i in range(data.num_instances):
        cluster_index_of_inst.append(int(clusterer.cluster_instance(data.get_instance(i))))

    sum_silhouette_coefficients = 0.0
    for i in range(data.num_instances):
        # Compute average distance of current instance to each cluster, including its own cluster
        average_distance_per_cluster = [0 for x in range(clusterer.number_of_clusters)]
        num_instances_per_cluster = [0 for x in range(clusterer.number_of_clusters)]
        for j in range(data.num_instances):
            average_distance_per_cluster[cluster_index_of_inst[j]] += dist_func.distance(data.get_instance(i), data.get_instance(j))
            num_instances_per_cluster[cluster_index_of_inst[j]] += 1 # Should the current instance be skipped though?
        for k in range(len(average_distance_per_cluster)):
            average_distance_per_cluster[k] /= num_instances_per_cluster[k]

        # Average distance to instance's own cluster
        a =  average_distance_per_cluster[cluster_index_of_inst[i]]

        # Find the distance of the "closest" other cluster
        average_distance_per_cluster[cluster_index_of_inst[i]] = sys.float_info.max
        b = min(average_distance_per_cluster)

        # Compute silhouette coefficient for current instance
        sum_silhouette_coefficients += ((b - a) / max(a, b)) if (clusterer.number_of_clusters > 1) else 0

    return sum_silhouette_coefficients / data.num_instances


def main(args=None):
    """
    Runs a clusterer from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Performs clustering from the command-line. Calls JVM start/stop automatically.',
        prog='pww-clusterer')
    parser.add_argument("-j", metavar="classpath", dest="classpath", help="additional classpath, jars/directories")
    parser.add_argument("-X", metavar="heap", dest="heap", help="max heap size for jvm, e.g., 512m")
    parser.add_argument("-t", metavar="train", dest="train", required=True, help="training set file")
    parser.add_argument("-T", metavar="test", dest="test", help="test set file")
    parser.add_argument("-d", metavar="outmodel", dest="outmodel", help="model output file name")
    parser.add_argument("-l", metavar="inmodel", dest="inmodel", help="model input file name")
    parser.add_argument("-p", metavar="attributes", dest="attributes", help="attribute range")
    parser.add_argument("-x", metavar="num folds", dest="numfolds", help="number of folds")
    parser.add_argument("-s", metavar="seed", dest="seed", help="seed value for randomization")
    parser.add_argument("-c", metavar="class index", dest="classindex", help="1-based class attribute index")
    parser.add_argument("-g", metavar="graph", dest="graph", help="graph output file (if supported)")
    parser.add_argument("clusterer", help="clusterer classname, e.g., weka.clusterers.SimpleKMeans")
    parser.add_argument("option", nargs=argparse.REMAINDER, help="additional clusterer options")
    parsed = parser.parse_args(args=args)
    jars = []
    if parsed.classpath is not None:
        jars = parsed.classpath.split(os.pathsep)
    params = []
    if parsed.train is not None:
        params.extend(["-t", parsed.train])
    if parsed.test is not None:
        params.extend(["-T", parsed.test])
    if parsed.outmodel is not None:
        params.extend(["-d", parsed.outmodel])
    if parsed.inmodel is not None:
        params.extend(["-l", parsed.inmodel])
    if parsed.attributes is not None:
        params.extend(["-p", parsed.attributes])
    if parsed.numfolds is not None:
        params.extend(["-x", parsed.numfolds])
    if parsed.seed is not None:
        params.extend(["-s", parsed.seed])
    if parsed.classindex is not None:
        params.extend(["-c", parsed.classindex])
    if parsed.graph is not None:
        params.extend(["-g", parsed.graph])

    jvm.start(jars, max_heap_size=parsed.heap, packages=True)

    logger.info("Commandline: " + join_options(sys.argv[1:]))

    try:
        clusterer = Clusterer(classname=parsed.clusterer)
        if len(parsed.option) > 0:
            clusterer.options = parsed.option
        print(ClusterEvaluation.evaluate_clusterer(clusterer, params))
    except Exception:
        print(traceback.format_exc())
    finally:
        jvm.stop()


def sys_main():
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    :rtype: int
    """

    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
