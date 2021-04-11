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
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import os
import sys
import argparse
import traceback
import weka.core.jvm as jvm
import weka.core.classes as classes
from weka.core.classes import serialization_write, serialization_read_all, serialization_write_all
from weka.core.classes import JavaObject, join_options
from weka.core.classes import OptionHandler
from weka.core.classes import Random
from weka.core.capabilities import Capabilities
from weka.core.dataset import Instances
from weka.filters import Filter

# logging setup
logger = logging.getLogger("weka.clusterers")


class Clusterer(OptionHandler):
    """
    Wrapper class for clusterers.
    """

    def __init__(self, classname="weka.clusterers.SimpleKMeans", jobject=None, options=None):
        """
        Initializes the specified clusterer using either the classname or the supplied JB_Object.

        :param classname: the classname of the clusterer
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
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
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        super(Clusterer, self)._make_calls()
        self._mc_cluster = javabridge.make_call(self.jobject, "clusterInstance", "(Lweka/core/Instance;)I")
        self._mc_distribution = javabridge.make_call(self.jobject, "distributionForInstance", "(Lweka/core/Instance;)[D")

    @property
    def capabilities(self):
        """
        Returns the capabilities of the clusterer.

        :return: the capabilities
        :rtype: Capabilities
        """
        return Capabilities(javabridge.call(self.jobject, "getCapabilities", "()Lweka/core/Capabilities;"))

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
        javabridge.call(self.jobject, "buildClusterer", "(Lweka/core/Instances;)V", data.jobject)

    def update_clusterer(self, inst):
        """
        Updates the clusterer with the instance.

        :param inst: the Instance to update the clusterer with
        :type inst: Instance
        """
        if self.is_updateable:
            javabridge.call(self.jobject, "updateClusterer", "(Lweka/core/Instance;)V", inst.jobject)
        else:
            logger.critical(classes.get_classname(self.jobject) + " is not updateable!")

    def update_finished(self):
        """
        Signals the clusterer that updating with new data has finished.
        """
        if self.is_updateable:
            javabridge.call(self.jobject, "updateFinished", "()V")
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
        :rtype: float[]
        """
        pred = self._mc_distribution(inst.jobject)
        return javabridge.get_env().get_double_array_elements(pred)

    @property
    def number_of_clusters(self):
        """
        Returns the number of clusters found.

        :return: the number fo clusters
        :rtype: int
        """
        return javabridge.call(self.jobject, "numberOfClusters", "()I")

    @property
    def graph_type(self):
        """
        Returns the graph type if classifier implements weka.core.Drawable, otherwise -1.

        :return: the type
        :rtype: int
        """
        if self.is_drawable:
            return javabridge.call(self.jobject, "graphType", "()I")
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
            return javabridge.call(self.jobject, "graph", "()Ljava/lang/String;")
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
        return Clusterer(
            jobject=javabridge.static_call(
                "weka/clusterers/AbstractClusterer", "makeCopy",
                "(Lweka/clusterers/Clusterer;)Lweka/clusterers/Clusterer;", clusterer.jobject))

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
        Initializes the specified clusterer using either the classname or the supplied JB_Object.

        :param classname: the classname of the clusterer
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
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
        return Clusterer(jobject=javabridge.call(self.jobject, "getClusterer", "()Lweka/clusterers/Clusterer;"))

    @clusterer.setter
    def clusterer(self, clusterer):
        """
        Sets the base clusterer.

        :param clusterer: the base clusterer to use
        :type clusterer: Clusterer
        """
        javabridge.call(self.jobject, "setClusterer", "(Lweka/clusterers/Clusterer;)V", clusterer.jobject)


class FilteredClusterer(SingleClustererEnhancer):
    """
    Wrapper class for the filtered clusterer.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified clusterer using either the classname or the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
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
        :rtype: Filter
        """
        return Filter(jobject=javabridge.call(self.jobject, "getFilter", "()Lweka/filters/Filter;"))

    @filter.setter
    def filter(self, filtr):
        """
        Sets the filter.

        :param filtr: the filter to use
        :type filtr: Filter
        """
        javabridge.call(self.jobject, "setFilter", "(Lweka/filters/Filter;)V", filtr.jobject)


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
        javabridge.call(self.jobject, "setClusterer", "(Lweka/clusterers/Clusterer;)V", clusterer.jobject)

    def test_model(self, test):
        """
        Evaluates the currently set clusterer on the test set.

        :param test: the test set to use for evaluating
        :type test: Instances
        """
        javabridge.call(self.jobject, "evaluateClusterer", "(Lweka/core/Instances;)V", test.jobject)

    @property
    def cluster_results(self):
        """
        The cluster results as string.

        :return: the results string
        :rtype: str
        """
        return javabridge.call(self.jobject, "clusterResultsToString", "()Ljava/lang/String;")

    @property
    def cluster_assignments(self):
        """
        Return an array of cluster assignments corresponding to the most recent set of instances clustered.

        :return: the cluster assignments
        :rtype: ndarray
        """
        array = javabridge.call(self.jobject, "getClusterAssignments", "()[D")
        if array is None:
            return None
        else:
            return javabridge.get_env().get_double_array_elements(array)

    @property
    def num_clusters(self):
        """
        Returns the number of clusters.

        :return: the number of clusters
        :rtype: int
        """
        return javabridge.call(self.jobject, "getNumClusters", "()I")

    @property
    def log_likelihood(self):
        """
        Returns the log likelihood.

        :return: the log likelihood
        :rtype: float
        """
        return javabridge.call(self.jobject, "getLogLikelihood", "()D")

    @property
    def classes_to_clusters(self):
        """
        Return the array (ordered by cluster number) of minimum error class to cluster mappings.

        :return: the mappings
        :rtype: ndarray
        """
        array = javabridge.call(self.jobject, "getClassesToClusters", "()[I")
        if array is None:
            return None
        else:
            return javabridge.get_env().get_int_array_elements(array)

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
        return javabridge.static_call(
            "Lweka/clusterers/ClusterEvaluation;", "evaluateClusterer",
            "(Lweka/clusterers/Clusterer;[Ljava/lang/String;)Ljava/lang/String;",
            clusterer.jobject, args)

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
        return javabridge.static_call(
            "Lweka/clusterers/ClusterEvaluation;", "crossValidateModel",
            "(Lweka/clusterers/DensityBasedClusterer;Lweka/core/Instances;ILjava/util/Random;)D",
            clusterer.jobject, data.jobject, num_folds, rnd.jobject)


def main(args=None):
    """
    Runs a clusterer from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Performs clustering from the command-line. Calls JVM start/stop automatically.')
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

    logger.debug("Commandline: " + join_options(sys.argv[1:]))

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
