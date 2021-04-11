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

# attribute_selection.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import argparse
import os
import sys
import traceback
import weka.core.jvm as jvm
import weka.core.typeconv as typeconv
from weka.core.classes import JavaObject, join_options
from weka.core.classes import OptionHandler
from weka.core.capabilities import Capabilities
from weka.core.dataset import Instances, Instance

# logging setup
logger = logging.getLogger("weka.attribute_selection")


class ASSearch(OptionHandler):
    """
    Wrapper class for attribute selection search algorithm.
    """

    def __init__(self, classname="weka.attributeSelection.BestFirst", jobject=None, options=None):
        """
        Initializes the specified search algorithm using either the classname or the supplied JB_Object.

        :param classname: the classname of the search algorithms
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = ASSearch.new_instance(classname)
        self.enforce_type(jobject, "weka.attributeSelection.ASSearch")
        self._header = None
        super(ASSearch, self).__init__(jobject=jobject, options=options)

    @property
    def header(self):
        """
        Returns the header of the training data.

        :return: the structure of the training data, None if not available
        :rtype: Instances
        """
        return self._header

    def search(self, evaluation, data):
        """
        Performs the search and returns the indices of the selected attributes.

        :param evaluation: the evaluation algorithm to use
        :type evaluation: ASEvaluation
        :param data: the data to use
        :type data: Instances
        :return: the selected attributes (0-based indices)
        :rtype: ndarray
        """
        array = javabridge.call(
            self.jobject, "search", "(Lweka/attributeSelection/ASEvaluation;Lweka/core/Instances;)[I",
            evaluation.jobject, data.jobject)
        self._header = data.copy_structure()
        if array is None:
            return None
        else:
            javabridge.get_env().get_int_array_elements(array)


class ASEvaluation(OptionHandler):
    """
    Wrapper class for attribute selection evaluation algorithm.
    """

    def __init__(self, classname="weka.attributeSelection.CfsSubsetEval", jobject=None, options=None):
        """
        Initializes the specified search algorithm using either the classname or the supplied JB_Object.

        :param classname: the classname of the search algorithms
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = ASEvaluation.new_instance(classname)
        self.enforce_type(jobject, "weka.attributeSelection.ASEvaluation")
        self.is_attribute_transformer = self.check_type(jobject, "weka.attributeSelection.AttributeTransformer")
        self._header = None
        super(ASEvaluation, self).__init__(jobject=jobject, options=options)

    @property
    def capabilities(self):
        """
        Returns the capabilities of the classifier.

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

    def build_evaluator(self, data):
        """
        Builds the evaluator with the data.

        :param data: the data to use
        :type data: Instances
        """
        self._header = data.copy_structure()
        javabridge.call(self.jobject, "buildEvaluator", "(Lweka/core/Instances;)V", data.jobject)

    def post_process(self, indices):
        """
        Post-processes the evaluator with the selected attribute indices.

        :param indices: the attribute indices list to use
        :type indices: ndarray
        :return: the processed indices
        :rtype: ndarray
        """
        array = javabridge.call(self.jobject, "postProcess", "([I)[I", indices)
        if array is None:
            return None
        else:
            return javabridge.get_env().get_int_array_elements(array)

    def transformed_header(self):
        """
        Returns just the header for the transformed data (ie. an empty set of instances. This is so that
        AttributeSelection can determine the structure of the transformed data without actually having to
        get all the transformed data through transformed_data().
        Returns None if not a weka.attributeSelection.AttributeTransformer

        :return: the header
        :rtype: Instances
        """
        if self.is_attribute_transformer:
            return Instances(javabridge.call(self.jobject, "transformedHeader", "()Lweka/core/Instances;"))
        else:
            return None

    def transformed_data(self, data):
        """
        Transform the supplied data set (assumed to be the same format as the training data).

        :param data: the data to transform
        :type data: Instances
        :return: the transformed data
        :rtype: Instances
        """
        if self.is_attribute_transformer:
            return Instances(javabridge.call(self.jobject, "transformedData", "(Lweka/core/Instances;)Lweka/core/Instances;", data.jobject))
        else:
            return None

    def convert_instance(self, inst):
        """
        Transforms an instance in the format of the original data to the transformed space.

        :param inst: the Instance to transform
        :type inst: Instance
        :return: the transformed instance
        :rtype: Instance
        """
        if self.is_attribute_transformer:
            return Instance(javabridge.call(self.jobject, "convertInstance", "(Lweka/core/Instance;)Lweka/core/Instance;", inst.jobject))
        else:
            return None


class AttributeSelection(JavaObject):
    """
    Performs attribute selection using search and evaluation algorithms.
    """

    def __init__(self):
        """
        Initializes the attribute selection.
        """
        jobject = AttributeSelection.new_instance("weka.attributeSelection.AttributeSelection")
        super(AttributeSelection, self).__init__(jobject)

    def evaluator(self, evaluator):
        """
        Sets the evaluator to use.

        :param evaluator: the evaluator to use.
        :type evaluator: ASEvaluation
        """
        javabridge.call(self.jobject, "setEvaluator", "(Lweka/attributeSelection/ASEvaluation;)V", evaluator.jobject)

    def search(self, search):
        """
        Sets the search algorithm to use.

        :param search: the search algorithm
        :type search: ASSearch
        """
        javabridge.call(self.jobject, "setSearch", "(Lweka/attributeSelection/ASSearch;)V", search.jobject)

    def folds(self, folds):
        """
        Sets the number of folds to use for cross-validation.

        :param folds: the number of folds
        :type folds: int
        """
        javabridge.call(self.jobject, "setFolds", "(I)V", folds)

    def ranking(self, ranking):
        """
        Sets whether to perform a ranking, if possible.

        :param ranking: whether to perform a ranking
        :type ranking: bool
        """
        javabridge.call(self.jobject, "setRanking", "(Z)V", ranking)

    def seed(self, seed):
        """
        Sets the seed for cross-validation.

        :param seed: the seed value
        :type seed: int
        """
        javabridge.call(self.jobject, "setSeed", "(I)V", seed)

    def crossvalidation(self, crossvalidation):
        """
        Sets whether to perform cross-validation.

        :param crossvalidation: whether to perform cross-validation
        :type crossvalidation: bool
        """
        javabridge.call(self.jobject, "setXval", "(Z)V", crossvalidation)

    def select_attributes(self, instances):
        """
        Performs attribute selection on the given dataset.

        :param instances: the data to process
        :type instances: Instances
        """
        javabridge.call(self.jobject, "SelectAttributes", "(Lweka/core/Instances;)V", instances.jobject)

    def select_attributes_cv_split(self, instances):
        """
        Performs attribute selection on the given cross-validation split.

        :param instances: the data to process
        :type instances: Instances
        """
        javabridge.call(self.jobject, "selectAttributesCVSplit", "(Lweka/core/Instances;)V", instances.jobject)

    @property
    def selected_attributes(self):
        """
        Returns the selected attributes from the last run.

        :return: the Numpy array of 0-based indices
        :rtype: ndarray
        """
        array = javabridge.call(self.jobject, "selectedAttributes", "()[I")
        if array is None:
            return None
        else:
            return javabridge.get_env().get_int_array_elements(array)

    @property
    def results_string(self):
        """
        Generates a results string from the last attribute selection.

        :return: the results string
        :rtype: str
        """
        return javabridge.call(self.jobject, "toResultsString", "()Ljava/lang/String;")

    @property
    def cv_results(self):
        """
        Generates a results string from the last cross-validation attribute selection.

        :return: the results string
        :rtype: str
        """
        return javabridge.call(self.jobject, "CVResultsString", "()Ljava/lang/String;")

    @property
    def number_attributes_selected(self):
        """
        Returns the number of attributes that were selected.

        :return: the number of attributes
        :rtype: int
        """
        return javabridge.call(self.jobject, "numberAttributesSelected", "()I")

    @property
    def ranked_attributes(self):
        """
        Returns the matrix of ranked attributes from the last run.

        :return: the Numpy matrix
        :rtype: ndarray
        """
        matrix = javabridge.call(self.jobject, "rankedAttributes", "()[[D")
        if matrix is None:
            return None
        else:
            return typeconv.jdouble_matrix_to_ndarray(matrix)

    def reduce_dimensionality(self, data):
        """
        Reduces the dimensionality of the provided Instance or Instances object.

        :param data: the data to process
        :type data: Instances
        :return: the reduced dataset
        :rtype: Instances
        """
        if type(data) is Instance:
            return Instance(
                javabridge.call(
                    self.jobject, "reduceDimensionality",
                    "(Lweka/core/Instance;)Lweka/core/Instance;", data.jobject))
        else:
            return Instances(
                javabridge.call(
                    self.jobject, "reduceDimensionality",
                    "(Lweka/core/Instances;)Lweka/core/Instances;", data.jobject))

    @classmethod
    def attribute_selection(cls, evaluator, args):
        """
        Performs attribute selection using the given attribute evaluator and options.

        :param evaluator: the evaluator to use
        :type evaluator: ASEvaluation
        :param args: the command-line args for the attribute selection
        :type args: list
        :return: the results string
        :rtype: str
        """
        return javabridge.static_call(
            "Lweka/attributeSelection/AttributeSelection;", "SelectAttributes",
            "(Lweka/attributeSelection/ASEvaluation;[Ljava/lang/String;)Ljava/lang/String;",
            evaluator.jobject, args)


def main(args=None):
    """
    Runs attribute selection from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Performs attribute selection from the command-line. Calls JVM start/stop automatically.')
    parser.add_argument("-j", metavar="classpath", dest="classpath", help="additional classpath, jars/directories")
    parser.add_argument("-X", metavar="heap", dest="heap", help="max heap size for jvm, e.g., 512m")
    parser.add_argument("-i", metavar="input", dest="input", required=True, help="input file")
    parser.add_argument("-c", metavar="class index", dest="classindex", help="1-based class attribute index")
    parser.add_argument("-s", metavar="search", dest="search", help="search method, classname and options")
    parser.add_argument("-x", metavar="num folds", dest="numfolds", help="number of folds")
    parser.add_argument("-n", metavar="seed", dest="seed", help="the seed value for randomization")
    parser.add_argument("evaluator", help="evaluator classname, e.g., weka.attributeSelection.CfsSubsetEval")
    parser.add_argument("option", nargs=argparse.REMAINDER, help="additional evaluator options")
    parsed = parser.parse_args(args=args)
    jars = []
    if parsed.classpath is not None:
        jars = parsed.classpath.split(os.pathsep)
    params = []
    if parsed.input is not None:
        params.extend(["-i", parsed.input])
    if parsed.classindex is not None:
        params.extend(["-c", parsed.classindex])
    if parsed.search is not None:
        params.extend(["-s", parsed.search])
    if parsed.numfolds is not None:
        params.extend(["-x", parsed.numfolds])
    if parsed.seed is not None:
        params.extend(["-n", parsed.seed])

    jvm.start(jars, max_heap_size=parsed.heap, packages=True)

    logger.debug("Commandline: " + join_options(sys.argv[1:]))

    try:
        evaluation = ASEvaluation(classname=parsed.evaluator)
        if len(parsed.option) > 0:
            evaluation.options = parsed.option
        print(AttributeSelection.attribute_selection(evaluation, params))
    except Exception as e:
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
    except Exception as ex:
        print(traceback.format_exc())
