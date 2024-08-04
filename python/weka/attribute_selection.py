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
# Copyright (C) 2014-2024 Fracpete (pythonwekawrapper at gmail dot com)

import logging
import argparse
import os
import sys
import traceback
import weka.core.jvm as jvm
import weka.core.typeconv as typeconv
from jpype import JClass
from weka.core.classes import JavaObject, join_options
from weka.core.classes import OptionHandler
from weka.core.capabilities import Capabilities
from weka.core.dataset import Instances, Instance

# logging setup
logger = logging.getLogger("weka.attribute_selection")
logger.setLevel(logging.INFO)


class ASSearch(OptionHandler):
    """
    Wrapper class for attribute selection search algorithm.
    """

    def __init__(self, classname="weka.attributeSelection.BestFirst", jobject=None, options=None):
        """
        Initializes the specified search algorithm using either the classname or the supplied JPype object.

        :param classname: the classname of the search algorithms
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        array = self.jobject.search(evaluation.jobject, data.jobject)
        self._header = data.copy_structure()
        if array is None:
            return None
        else:
            return typeconv.jint_array_to_ndarray(array)


class ASEvaluation(OptionHandler):
    """
    Wrapper class for attribute selection evaluation algorithm.
    """

    def __init__(self, classname="weka.attributeSelection.CfsSubsetEval", jobject=None, options=None):
        """
        Initializes the specified search algorithm using either the classname or the supplied JPype object.

        :param classname: the classname of the search algorithms
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        return Capabilities(self.jobject.getCapabilities())

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
        self.jobject.buildEvaluator(data.jobject)

    def post_process(self, indices):
        """
        Post-processes the evaluator with the selected attribute indices.

        :param indices: the attribute indices list to use
        :type indices: ndarray
        :return: the processed indices
        :rtype: ndarray
        """
        array = self.jobject.postProcess(indices)
        if array is None:
            return None
        else:
            return typeconv.jint_array_to_ndarray(array)

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
            return Instances(self.jobject.transformedHeader())
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
            return Instances(self.jobject.transformedData(data.jobject))
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
            return Instance(self.jobject.convertInstance(inst.jobject))
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
        self._cv_results = None

    def evaluator(self, evaluator):
        """
        Sets the evaluator to use.

        :param evaluator: the evaluator to use.
        :type evaluator: ASEvaluation
        """
        self.jobject.setEvaluator(evaluator.jobject)

    def search(self, search):
        """
        Sets the search algorithm to use.

        :param search: the search algorithm
        :type search: ASSearch
        """
        self.jobject.setSearch(search.jobject)

    def folds(self, folds):
        """
        Sets the number of folds to use for cross-validation.

        :param folds: the number of folds
        :type folds: int
        """
        self.jobject.setFolds(folds)

    def ranking(self, ranking):
        """
        Sets whether to perform a ranking, if possible.

        :param ranking: whether to perform a ranking
        :type ranking: bool
        """
        self.jobject.setRanking(ranking)

    def seed(self, seed):
        """
        Sets the seed for cross-validation.

        :param seed: the seed value
        :type seed: int
        """
        self.jobject.setSeed(seed)

    def crossvalidation(self, crossvalidation):
        """
        Sets whether to perform cross-validation.

        :param crossvalidation: whether to perform cross-validation
        :type crossvalidation: bool
        """
        self.jobject.setXval(crossvalidation)

    def select_attributes(self, instances):
        """
        Performs attribute selection on the given dataset.

        :param instances: the data to process
        :type instances: Instances
        """
        self._cv_results = None
        self.jobject.SelectAttributes(instances.jobject)

    def select_attributes_cv_split(self, instances):
        """
        Performs attribute selection on the given cross-validation split.

        :param instances: the data to process
        :type instances: Instances
        """
        self.jobject.selectAttributesCVSplit(instances.jobject)

    @property
    def selected_attributes(self):
        """
        Returns the selected attributes from the last run.

        :return: the Numpy array of 0-based indices
        :rtype: ndarray
        """
        array = self.jobject.selectedAttributes()
        if array is None:
            return None
        else:
            return typeconv.jint_array_to_ndarray(array)

    @property
    def results_string(self):
        """
        Generates a results string from the last attribute selection.

        :return: the results string
        :rtype: str
        """
        return self.jobject.toResultsString()

    @property
    def cv_results(self):
        """
        Generates a results string from the last cross-validation attribute selection.

        :return: the results string
        :rtype: str
        """
        if self._cv_results is None:
            self._cv_results = self.jobject.CVResultsString()
        return self._cv_results

    @property
    def subset_results(self):
        """
        Returns the results from the cross-validation subsets, i.e., how often
        an attribute was selected.

        Unfortunately, the Weka API does not give direct access to underlying
        data structures, hence we have to parse the textual output.

        :return: the list of results (double)
        :rtype: list
        """
        if self._cv_results is None:
            raise Exception("No attribute selection performed?")
        lines = self._cv_results.split("\n")

        # ranking or subset eval?
        start = 0
        for i, l in enumerate(lines):
            if "average merit" in l:
                raise Exception("Cannot parse output from ranker!")
            elif "number of folds" in l:
                start = i + 1
                break

        # parse text
        result = []
        for i in range(start, len(lines)):
            l = lines[i]
            if "(" in l:
                result.append(float(l[0:l.index("(")].strip()))

        return result

    @property
    def rank_results(self):
        """
        Returns the results from the cross-validation for rankers.

        Unfortunately, the Weka API does not give direct access to underlying
        data structures, hence we have to parse the textual output.

        :return: the dictionary of results (mean and stdev for rank and merit)
        :rtype: dict
        """
        if self._cv_results is None:
            raise Exception("No attribute selection performed?")
        lines = self.cv_results.split("\n")

        # ranking or subset eval?
        start = 0
        for i, l in enumerate(lines):
            if "average merit" in l:
                start = i + 1
                break
            elif "number of folds" in l:
                raise Exception("Cannot parse output from non-rankers!")

        # parse text
        merit_mean = []
        merit_stdev = []
        rank_mean = []
        rank_stdev = []
        for i in range(start, len(lines)):
            l = lines[i]
            if "+-" in l:
                parts = l.split(" +- ")
                inner = None
                right = None
                if len(parts) == 3:
                    inner = [x for x in parts[1].split(" ") if x]
                    right = [x for x in parts[2].split(" ") if x]
                if (len(inner) == 2) and (len(right) > 2):
                    merit_mean.append(float(parts[0]))
                    merit_stdev.append(float(inner[0]))
                    rank_mean.append(float(inner[1]))
                    rank_stdev.append(float(right[0]))

        result = {
            "merit_mean": merit_mean,
            "merit_stdev": merit_stdev,
            "rank_mean": rank_mean,
            "rank_stdev": rank_stdev,
        }

        return result

    @property
    def number_attributes_selected(self):
        """
        Returns the number of attributes that were selected.

        :return: the number of attributes
        :rtype: int
        """
        return self.jobject.numberAttributesSelected()

    @property
    def ranked_attributes(self):
        """
        Returns the matrix of ranked attributes from the last run.

        :return: the Numpy matrix
        :rtype: ndarray
        """
        matrix = self.jobject.rankedAttributes()
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
            return Instance(self.jobject.reduceDimensionality(data.jobject))
        else:
            return Instances(self.jobject.reduceDimensionality(data.jobject))

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
        return JClass("weka.attributeSelection.AttributeSelection").SelectAttributes(evaluator.jobject, args)


def main(args=None):
    """
    Runs attribute selection from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Performs attribute selection from the command-line. Calls JVM start/stop automatically.',
        prog='pww-attsel')
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

    logger.info("Commandline: " + join_options(sys.argv[1:]))

    try:
        evaluation = ASEvaluation(classname=parsed.evaluator)
        if len(parsed.option) > 0:
            evaluation.options = parsed.option
        print(AttributeSelection.attribute_selection(evaluation, params))
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
    except Exception as ex:
        print(traceback.format_exc())
