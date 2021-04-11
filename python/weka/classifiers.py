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

import sys
import os
import javabridge
import logging
import argparse
import traceback
import weka.core.jvm as jvm
import weka.core.typeconv as typeconv
import weka.core.classes as classes
from numpy import *
from weka.core.classes import JavaObject, join_options, OptionHandler, Random, SelectedTag, Tags, Tag, JavaArray, \
    is_instance_of
from weka.core.classes import AbstractParameter
from weka.core.classes import serialization_write, serialization_read_all, serialization_write_all
from weka.core.capabilities import Capabilities
from weka.core.dataset import Instances, Instance, Attribute
from weka.filters import Filter
from weka.attribute_selection import ASEvaluation, ASSearch

# logging setup
logger = logging.getLogger("weka.classifiers")


class Classifier(OptionHandler):
    """
    Wrapper class for classifiers.
    """

    def __init__(self, classname="weka.classifiers.rules.ZeroR", jobject=None, options=None):
        """
        Initializes the specified classifier using either the classname or the supplied JB_Object.

        :param classname: the classname of the classifier
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Classifier.new_instance(classname)
        self.enforce_type(jobject, "weka.classifiers.Classifier")
        self.is_updateable = self.check_type(jobject, "weka.classifiers.UpdateableClassifier")
        self.is_drawable = self.check_type(jobject, "weka.core.Drawable")
        self.is_batchpredictor = self.check_type(jobject, "weka.core.BatchPredictor")
        self._header = None
        super(Classifier, self).__init__(jobject=jobject, options=options)

    def _make_calls(self):
        """
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        super(Classifier, self)._make_calls()
        self._mc_classify = javabridge.make_call(self.jobject, "classifyInstance", "(Lweka/core/Instance;)D")
        self._mc_distribution = javabridge.make_call(self.jobject, "distributionForInstance", "(Lweka/core/Instance;)[D")
        if self.is_batchpredictor:
            self._mc_distributions = javabridge.make_call(
                self.jobject, "distributionsForInstances", "(Lweka/core/Instances;)[[D")

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

    def build_classifier(self, data):
        """
        Builds the classifier with the data.

        :param data: the data to train the classifier with
        :type data: Instances
        """
        self._header = data.copy_structure()
        javabridge.call(self.jobject, "buildClassifier", "(Lweka/core/Instances;)V", data.jobject)

    def update_classifier(self, inst):
        """
        Updates the classifier with the instance.

        :param inst: the Instance to update the classifier with
        :type inst: Instance
        """
        if self.is_updateable:
            javabridge.call(self.jobject, "updateClassifier", "(Lweka/core/Instance;)V", inst.jobject)
        else:
            logger.critical(classes.get_classname(self.jobject) + " is not updateable!")

    def classify_instance(self, inst):
        """
        Peforms a prediction.

        :param inst: the Instance to get a prediction for
        :type inst: Instance
        :return: the classification (either regression value or 0-based label index)
        :rtype: float
        """
        return self._mc_classify(inst.jobject)

    def distribution_for_instance(self, inst):
        """
        Peforms a prediction, returning the class distribution.

        :param inst: the Instance to get the class distribution for
        :type inst: Instance
        :return: the class distribution array
        :rtype: ndarray
        """
        pred = self._mc_distribution(inst.jobject)
        return javabridge.get_env().get_double_array_elements(pred)

    def distributions_for_instances(self, data):
        """
        Peforms predictions, returning the class distributions.

        :param data: the Instances to get the class distributions for
        :type data: Instances
        :return: the class distribution matrix, None if not a batch predictor
        :rtype: ndarray
        """
        if self.is_batchpredictor:
            return typeconv.jdouble_matrix_to_ndarray(self._mc_distributions(data.jobject))
        else:
            return None

    @property
    def batch_size(self):
        """
        Returns the batch size, in case this classifier is a batch predictor.

        :return: the batch size, None if not a batch predictor
        :rtype: str
        """
        if self.is_batchpredictor:
            return javabridge.call(self.jobject, "getBatchSize", "()Ljava/lang/String;")
        else:
            return None

    @batch_size.setter
    def batch_size(self, size):
        """
        Sets the batch size, in case this classifier is a batch predictor.

        :param size: the size of the batch
        :type size: str
        """
        if self.is_batchpredictor:
            javabridge.call(self.jobject, "setBatchSize", "(Ljava/lang/String;)V", size)

    def has_efficient_batch_prediction(self):
        """
        Returns whether the classifier implements a more efficient batch prediction.

        :return: True if a more efficient batch prediction is implemented, always False if not batch predictor
        :rtype: bool
        """
        if self.is_batchpredictor:
            return javabridge.call(self.jobject, "implementsMoreEfficientBatchPrediction", "()Z")
        else:
            return False

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

        :return: the generated graph string
        :rtype: str
        """
        if self.is_drawable:
            return javabridge.call(self.jobject, "graph", "()Ljava/lang/String;")
        else:
            return None

    def to_source(self, classname):
        """
        Returns the model as Java source code if the classifier implements weka.classifiers.Sourcable.

        :param classname: the classname for the generated Java code
        :type classname: str
        :return: the model as source code string
        :rtype: str
        """
        if not self.check_type(self.jobject, "weka.classifiers.Sourcable"):
            return None
        return javabridge.call(self.jobject, "toSource", "(Ljava/lang/String;)Ljava/lang/String;", classname)

    @classmethod
    def make_copy(cls, classifier):
        """
        Creates a copy of the classifier.

        :param classifier: the classifier to copy
        :type classifier: Classifier
        :return: the copy of the classifier
        :rtype: Classifier
        """
        return Classifier(
            jobject=javabridge.static_call(
                "weka/classifiers/AbstractClassifier", "makeCopy",
                "(Lweka/classifiers/Classifier;)Lweka/classifiers/Classifier;", classifier.jobject))

    @classmethod
    def deserialize(cls, ser_file):
        """
        Deserializes a classifier from a file.

        :param ser_file: the model file to deserialize
        :type ser_file: str
        :return: model and, if available, the dataset header
        :rtype: tuple
        """

        objs = serialization_read_all(ser_file)
        if len(objs) == 1:
            return Classifier(jobject=objs[0]), None
        elif len(objs) == 2:
            return Classifier(jobject=objs[0]), Instances(jobject=objs[1])
        else:
            raise Exception(
                "Excepted one or two objects in the model file (%s), but encountered: %d" % (ser_file, len(objs)))

    def serialize(self, ser_file, header=None):
        """
        Serializes the classifier to the specified file.

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


class SingleClassifierEnhancer(Classifier):
    """
    Wrapper class for classifiers that use a single base classifier.
    """

    def __init__(self, classname=None, jobject=None, options=None):
        """
        Initializes the specified classifier using either the classname or the supplied JB_Object.

        :param classname: the classname of the classifier
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Classifier.new_instance(classname)
        self.enforce_type(jobject, "weka.classifiers.SingleClassifierEnhancer")
        super(SingleClassifierEnhancer, self).__init__(classname=classname, jobject=jobject, options=options)

    @property
    def classifier(self):
        """
        Returns the base classifier.

        ;return: the base classifier
        :rtype: Classifier
        """
        return Classifier(jobject=javabridge.call(self.jobject, "getClassifier", "()Lweka/classifiers/Classifier;"))

    @classifier.setter
    def classifier(self, classifier):
        """
        Sets the base classifier.

        :param classifier: the base classifier to use
        :type classifier: Classifier
        """
        javabridge.call(self.jobject, "setClassifier", "(Lweka/classifiers/Classifier;)V", classifier.jobject)


class FilteredClassifier(SingleClassifierEnhancer):
    """
    Wrapper class for the filtered classifier.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified classifier using its classname or the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        classname = "weka.classifiers.meta.FilteredClassifier"
        if jobject is None:
            jobject = Classifier.new_instance(classname)
        else:
            self.enforce_type(jobject, classname)
        super(FilteredClassifier, self).__init__(jobject=jobject, options=options)

    @property
    def filter(self):
        """
        Returns the filter.

        :return: the filter in use
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

    def check_for_modified_class_attribute(self, check):
        """
        Sets whether to check for class attribute modifications.

        :param check: True if checking for modifications
        :type check: bool
        """
        javabridge.call(self.jobject, "setDoNotCheckForModifiedClassAttribute", "(Z)V", not check)


class AttributeSelectedClassifier(SingleClassifierEnhancer):
    """
    Wrapper class for the AttributeSelectedClassifier.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified classifier using its classname or the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        classname = "weka.classifiers.meta.AttributeSelectedClassifier"
        if jobject is None:
            jobject = Classifier.new_instance(classname)
        else:
            self.enforce_type(jobject, classname)
        super(AttributeSelectedClassifier, self).__init__(jobject=jobject, options=options)

    @property
    def evaluator(self):
        """
        Returns the evaluator.

        :return: the evaluator in use
        :rtype: ASEvaluation
        """
        return ASEvaluation(jobject=javabridge.call(self.jobject, "getEvaluator", "()Lweka/attributeSelection/ASEvaluation;"))

    @evaluator.setter
    def evaluator(self, evl):
        """
        Sets the evaluator.

        :param evl: the evaluator to use
        :type evl: ASEvaluation
        """
        javabridge.call(self.jobject, "setEvaluator", "(Lweka/attributeSelection/ASEvaluation;)V", evl.jobject)

    @property
    def search(self):
        """
        Returns the search.

        :return: the search in use
        :rtype: ASSearch
        """
        return ASSearch(jobject=javabridge.call(self.jobject, "getSearch", "()Lweka/attributeSelection/ASSearch;"))

    @search.setter
    def search(self, search):
        """
        Sets the search.

        :param search: the search to use
        :type search: ASSearch
        """
        javabridge.call(self.jobject, "setSearch", "(Lweka/attributeSelection/ASSearch;)V", search.jobject)


class GridSearch(SingleClassifierEnhancer):
    """
    Wrapper class for the GridSearch meta-classifier.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified classifier using its classname or the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        classname = "weka.classifiers.meta.GridSearch"
        if jobject is None:
            jobject = GridSearch.new_instance(classname)
            if jobject is None:
                raise Exception(
                    "Failed to instantiate GridSearch - package installed and jvm started with package support?")
        else:
            self.enforce_type(jobject, classname)
        super(GridSearch, self).__init__(jobject=jobject, options=options)
        self.tags_evaluation = Tags.get_tags("weka.classifiers.meta.GridSearch", "TAGS_EVALUATION")

    @property
    def evaluation(self):
        """
        Returns the currently set statistic used for evaluation.

        :return: the statistic
        :rtype: SelectedTag
        """
        return SelectedTag(
            javabridge.call(self.jobject, "getEvaluation", "()Lweka/core/SelectedTag;"))

    @evaluation.setter
    def evaluation(self, evl):
        """
        Sets the statistic to use for evaluation.

        :param evl: the statistic
        :type evl: SelectedTag, Tag or str
        """
        if isinstance(evl, str):
            evl = self.tags_evaluation.find(evl)
        if isinstance(evl, Tag):
            evl = SelectedTag(tag_id=evl.ident, tags=self.tags_evaluation)
        javabridge.call(self.jobject, "setEvaluation", "(Lweka/core/SelectedTag;)V", evl.jobject)

    @property
    def x(self):
        """
        Returns a dictionary with all the current values for the X of the grid.
        Keys for the dictionary: property, min, max, step, base, expression
        Types: property=str, min=float, max=float, step=float, base=float, expression=str

        :return: the dictionary with the parameters
        :rtype: dict
        """
        result = {}
        result["property"] = javabridge.call(self.jobject, "getXProperty", "()Ljava/lang/String;")
        result["min"] = javabridge.call(self.jobject, "getXMin", "()D")
        result["max"] = javabridge.call(self.jobject, "getXMax", "()D")
        result["step"] = javabridge.call(self.jobject, "getXStep", "()D")
        result["base"] = javabridge.call(self.jobject, "getXBase", "()D")
        result["expression"] = javabridge.call(self.jobject, "getXExpression", "()Ljava/lang/String;")
        return result

    @x.setter
    def x(self, d):
        """
        Allows to configure the X of the grid with one method call.
        Keys for the dictionary: property, min, max, step, base, expression
        Types: property=str, min=float, max=float, step=float, base=float, expression=str

        :param d: the dictionary with the parameters
        :type d: dict
        """
        if "property" in d:
            javabridge.call(self.jobject, "setXProperty", "(Ljava/lang/String;)V", d["property"])
        if "min" in d:
            javabridge.call(self.jobject, "setXMin", "(D)V", d["min"])
        if "max" in d:
            javabridge.call(self.jobject, "setXMax", "(D)V", d["max"])
        if "step" in d:
            javabridge.call(self.jobject, "setXStep", "(D)V", d["step"])
        if "base" in d:
            javabridge.call(self.jobject, "setXBase", "(D)V", d["base"])
        if "expression" in d:
            javabridge.call(self.jobject, "setXExpression", "(Ljava/lang/String;)V", d["expression"])

    @property
    def y(self):
        """
        Returns a dictionary with all the current values for the Y of the grid.
        Keys for the dictionary: property, min, max, step, base, expression
        Types: property=str, min=float, max=float, step=float, base=float, expression=str

        :return: the dictionary with the parameters
        :rtype: dict
        """
        result = {}
        result["property"] = javabridge.call(self.jobject, "getYProperty", "()Ljava/lang/String;")
        result["min"] = javabridge.call(self.jobject, "getYMin", "()D")
        result["max"] = javabridge.call(self.jobject, "getYMax", "()D")
        result["step"] = javabridge.call(self.jobject, "getYStep", "()D")
        result["base"] = javabridge.call(self.jobject, "getYBase", "()D")
        result["expression"] = javabridge.call(self.jobject, "getYExpression", "()Ljava/lang/String;")
        return result

    @y.setter
    def y(self, d):
        """
        Allows to configure the Y of the grid with one method call.
        Keys for the dictionary: property, min, max, step, base, expression
        Types: property=str, min=float, max=float, step=float, base=float, expression=str

        :param d: the dictionary with the parameters
        :type d: dict
        """
        if "property" in d:
            javabridge.call(self.jobject, "setYProperty", "(Ljava/lang/String;)V", d["property"])
        if "min" in d:
            javabridge.call(self.jobject, "setYMin", "(D)V", d["min"])
        if "max" in d:
            javabridge.call(self.jobject, "setYMax", "(D)V", d["max"])
        if "step" in d:
            javabridge.call(self.jobject, "setYStep", "(D)V", d["step"])
        if "base" in d:
            javabridge.call(self.jobject, "setYBase", "(D)V", d["base"])
        if "expression" in d:
            javabridge.call(self.jobject, "setYExpression", "(Ljava/lang/String;)V", d["expression"])

    @property
    def best(self):
        """
        Returns the best classifier setup found during the th search.

        :return: the best classifier setup
        :rtype: Classifier
        """
        return Classifier(jobject=javabridge.call(self.jobject, "getBestClassifier", "()Lweka/classifiers/Classifier;"))


class MultiSearch(SingleClassifierEnhancer):
    """
    Wrapper class for the MultiSearch meta-classifier.
    NB: 'multi-search-weka-package' must be installed (https://github.com/fracpete/multisearch-weka-package),
    version 2016.1.15 or later.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified classifier using its classname or the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        classname = "weka.classifiers.meta.MultiSearch"
        if jobject is None:
            jobject = MultiSearch.new_instance(classname)
        else:
            self.enforce_type(jobject, classname)
        super(MultiSearch, self).__init__(jobject=jobject, options=options)
        self.tags_evaluation = Tags.get_object_tags(self, "getMetricsTags")

    @property
    def evaluation(self):
        """
        Returns the currently set statistic used for evaluation.

        :return: the statistic
        :rtype: SelectedTag
        """
        return SelectedTag(
            javabridge.call(self.jobject, "getEvaluation", "()Lweka/core/SelectedTag;"))

    @evaluation.setter
    def evaluation(self, evl):
        """
        Sets the statistic to use for evaluation.

        :param evl: the statistic
        :type evl: SelectedTag, Tag or str
        """
        if isinstance(evl, str):
            evl = self.tags_evaluation.find(evl)
        if isinstance(evl, Tag):
            evl = SelectedTag(tag_id=evl.ident, tags=self.tags_evaluation)
        javabridge.call(self.jobject, "setEvaluation", "(Lweka/core/SelectedTag;)V", evl.jobject)

    @property
    def parameters(self):
        """
        Returns the list of currently set search parameters.

        :return: the list of AbstractSearchParameter objects
        :rtype: list
        """
        array = JavaArray(
            javabridge.call(self.jobject, "getSearchParameters", "()[Lweka/core/setupgenerator/AbstractParameter;"))
        result = []
        for item in array:
            result.append(AbstractParameter(jobject=item.jobject))
        return result

    @parameters.setter
    def parameters(self, params):
        """
        Sets the list of search parameters to use.

        :param params: list of AbstractSearchParameter objects
        :type params: list
        """
        array = JavaArray(JavaArray.new_instance("weka.core.setupgenerator.AbstractParameter", len(params)))
        for idx, obj in enumerate(params):
            array[idx] = obj.jobject
        javabridge.call(self.jobject, "setSearchParameters", "([Lweka/core/setupgenerator/AbstractParameter;)V", array.jobject)

    @property
    def best(self):
        """
        Returns the best classifier setup found during the th search.

        :return: the best classifier setup
        :rtype: Classifier
        """
        return Classifier(jobject=javabridge.call(self.jobject, "getBestClassifier", "()Lweka/classifiers/Classifier;"))


class MultipleClassifiersCombiner(Classifier):
    """
    Wrapper class for classifiers that use a multiple base classifiers.
    """

    def __init__(self, classname=None, jobject=None, options=None):
        """
        Initializes the specified classifier using either the classname or the supplied JB_Object.

        :param classname: the classname of the classifier
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: list of commandline options
        :type options: list
        """
        if jobject is None:
            jobject = Classifier.new_instance(classname)
        self.enforce_type(jobject, "weka.classifiers.MultipleClassifiersCombiner")
        super(MultipleClassifiersCombiner, self).__init__(classname=classname, jobject=jobject, options=options)

    @property
    def classifiers(self):
        """
        Returns the list of base classifiers.

        :return: the classifier list
        :rtype: list
        """
        objects = javabridge.get_env().get_object_array_elements(
            javabridge.call(self.jobject, "getClassifiers", "()[Lweka/classifiers/Classifier;"))
        result = []
        for obj in objects:
            result.append(Classifier(jobject=obj))
        return result

    @classifiers.setter
    def classifiers(self, classifiers):
        """
        Sets the base classifiers.

        :param classifiers: the list of base classifiers to use
        :type classifiers: list
        """
        obj = []
        for classifier in classifiers:
            obj.append(classifier.jobject)
        javabridge.call(self.jobject, "setClassifiers", "([Lweka/classifiers/Classifier;)V", obj)

    def clear(self):
        """
        Removes all classifiers.
        """
        self.classifiers = []

    def append(self, classifier):
        """
        Appends the classifier to the current list of classifiers.

        :param classifier: the classifier to add
        :type classifier: Classifier
        """
        l = self.classifiers
        l.append(classifier)
        self.classifiers = l


class Kernel(OptionHandler):
    """
    Wrapper class for kernels.
    """

    def __init__(self, classname=None, jobject=None, options=None):
        """
        Initializes the specified kernel using either the classname or the supplied JB_Object.

        :param classname: the classname of the kernel
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Classifier.new_instance(classname)
        self.enforce_type(jobject, "weka.classifiers.functions.supportVector.Kernel")
        super(Kernel, self).__init__(jobject=jobject, options=options)

    def capabilities(self):
        """
        Returns the capabilities of the classifier.

        :return: the capabilities
        :rtype: Capabilities
        """
        return Capabilities(javabridge.call(self.jobject, "getCapabilities", "()Lweka/core/Capabilities;"))

    @property
    def checks_turned_off(self):
        """
        Returns whether checks are turned off.

        :return: True if checks turned off
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getChecksTurnedOff", "()Z")

    @checks_turned_off.setter
    def checks_turned_off(self, off):
        """
        Turns any checks on/off.

        :param off: True to turn off checks
        :type off: bool
        """
        javabridge.call(self.jobject, "setChecksTurnedOff", "(Z)V", off)

    def clean(self):
        """
        Frees the memory used by the kernel.
        """
        javabridge.call(self.jobject, "clean", "()V")

    def build_kernel(self, data):
        """
        Builds the classifier with the data.

        :param data: the data to train the classifier with
        :type data: Instances
        """
        javabridge.call(self.jobject, "buildKernel", "(Lweka/core/Instances;)V", data.jobject)

    def eval(self, id1, id2, inst1):
        """
        Computes the result of the kernel function for two instances. If id1 == -1, eval use inst1 instead of an
        instance in the dataset.

        :param id1: the index of the first instance in the dataset
        :type id1: int
        :param id2: the index of the second instance in the dataset
        :type id2: int
        :param inst1: the instance corresponding to id1 (used if id1 == -1)
        :type inst1: Instance
        """
        jinst1 = None
        if inst1 is not None:
            jinst1 = inst1.jobject
        return javabridge.call(self.jobject, "eval", "(IILweka/core/Instance;)D", id1, id2, jinst1)

    @classmethod
    def make_copy(cls, kernel):
        """
        Creates a copy of the kernel.

        :param kernel: the kernel to copy
        :type kernel: Kernel
        :return: the copy of the kernel
        :rtype: Kernel
        """
        return Kernel(
            jobject=javabridge.static_call(
                "weka/classifiers/functions/supportVector/Kernel", "makeCopy",
                "(Lweka/classifiers/functions/supportVector/Kernel;)Lweka/classifiers/functions/supportVector/Kernel;",
                kernel.jobject))


class KernelClassifier(Classifier):
    """
    Wrapper class for classifiers that have a kernel property, like SMO.
    """

    def __init__(self, classname=None, jobject=None, options=None):
        """
        Initializes the specified classifier using either the classname or the supplied JB_Object.

        :param classname: the classname of the classifier
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: list of commandline options
        :type options: list
        """
        if jobject is None:
            jobject = Classifier.new_instance(classname)
        self.enforce_type(jobject, "weka.classifiers.Classifier")
        if not javabridge.static_call(
                "weka/classifiers/KernelHelper", "hasKernelProperty",
                "(Ljava/lang/Object;)Z",
                jobject):
            raise Exception("Does not handle a kernel: " + classes.get_classname(jobject))
        super(KernelClassifier, self).__init__(classname=classname, jobject=jobject, options=options)

    @property
    def kernel(self):
        """
        Returns the current kernel.

        :return: the kernel or None if none found
        :rtype: Kernel
        """
        result = javabridge.static_call(
            "weka/classifiers/KernelHelper", "getKernel",
            "(Ljava/lang/Object;)Lweka/classifiers/functions/supportVector/Kernel;",
            self.jobject)
        if result is None:
            return None
        else:
            return Kernel(jobject=result)

    @kernel.setter
    def kernel(self, kernel):
        """
        Sets the kernel.

        :param kernel: the kernel to set
        :type kernel: Kernel
        """
        result = javabridge.static_call(
            "weka/classifiers/KernelHelper", "setKernel",
            "(Ljava/lang/Object;Lweka/classifiers/functions/supportVector/Kernel;)Z",
            self.jobject, kernel.jobject)
        if not result:
            raise Exception("Failed to set kernel!")


class Prediction(JavaObject):
    """
    Wrapper class for a prediction.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the prediction to wrap
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.classifiers.evaluation.Prediction")
        super(Prediction, self).__init__(jobject)

    @property
    def actual(self):
        """
        Returns the actual value.

        :return: the actual value (internal representation)
        :rtype: float
        """
        return javabridge.call(self.jobject, "actual", "()D")

    @property
    def predicted(self):
        """
        Returns the predicted value.

        :return: the predicted value (internal representation)
        :rtype: float
        """
        return javabridge.call(self.jobject, "predicted", "()D")

    @property
    def weight(self):
        """
        Returns the weight.

        :return: the weight of the Instance that was used
        :rtype: float
        """
        return javabridge.call(self.jobject, "weight", "()D")


class NominalPrediction(Prediction):
    """
    Wrapper class for a nominal prediction.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the prediction to wrap
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.classifiers.evaluation.NominalPrediction")
        super(NominalPrediction, self).__init__(jobject)

    @property
    def distribution(self):
        """
        Returns the class distribution.

        :return: the class distribution list
        :rtype: ndarray
        """
        return javabridge.get_env().get_double_array_elements(javabridge.call(self.jobject, "distribution", "()[D"))

    @property
    def margin(self):
        """
        Returns the margin.

        :return: the margin
        :rtype: float
        """
        return javabridge.call(self.jobject, "margin", "()D")


class NumericPrediction(Prediction):
    """
    Wrapper class for a numeric prediction.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the prediction to wrap
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.classifiers.evaluation.NumericPrediction")
        super(NumericPrediction, self).__init__(jobject)

    @property
    def error(self):
        """
        Returns the error.

        :return: the error
        :rtype: float
        """
        return javabridge.call(self.jobject, "error", "()D")

    @property
    def prediction_intervals(self):
        """
        Returns the prediction intervals.

        :return: the intervals
        :rtype: ndarray
        """
        return typeconv.jdouble_matrix_to_ndarray(javabridge.call(self.jobject, "predictionIntervals", "()[[D"))


class CostMatrix(JavaObject):
    """
    Class for storing and manipulating a misclassification cost matrix. The element at position i,j in the matrix
    is the penalty for classifying an instance of class j as class i. Cost values can be fixed or computed on a
    per-instance basis (cost sensitive evaluation only) from the value of an attribute or an expression involving
    attribute(s).
    """

    def __init__(self, matrx=None, num_classes=None):
        """
        Initializes the matrix object.

        :param matrx: the matrix to copy
        :type matrx: CostMatrix or ndarray or JB_Object
        :param num_classes: the number of classes
        :type num_classes: int
        """
        if matrx is not None:
            if isinstance(matrx, CostMatrix):
                jobject = javabridge.make_instance(
                    "weka/classifiers/CostMatrix", "(Lweka/classifiers/CostMatrix;)V", matrx.jobject)
                super(CostMatrix, self).__init__(jobject)
            elif isinstance(matrx, ndarray):
                shp = matrx.shape
                if len(shp) != 2:
                    raise Exception("Numpy array must be a 2-dimensional array!")
                rows, cols = shp
                if rows == cols:
                    cmatrix = CostMatrix(num_classes=rows)
                    for r in range(rows):
                        for c in range(cols):
                            cmatrix.set_element(r, c, matrx[r][c])
                    super(CostMatrix, self).__init__(cmatrix.jobject)
                else:
                    raise Exception("Numpy array must be a square matrix!")
            elif isinstance(matrx, javabridge.JB_Object):
                super(CostMatrix, self).__init__(matrx)
            else:
                raise Exception(
                    "Matrix must be either a CostMatrix or a 2-dimensional numpy array: " + str(type(matrx)))
        elif not num_classes is None:
            jobject = javabridge.make_instance(
                "weka/classifiers/CostMatrix", "(I)V", num_classes)
            super(CostMatrix, self).__init__(jobject)
        else:
            raise Exception("Either matrix or number of classes must be provided!")

    def apply_cost_matrix(self, data, rnd):
        """
        Applies the cost matrix to the data.

        :param data: the data to apply to
        :type data: Instances
        :param rnd: the random number generator
        :type rnd: Random
        """
        return Instances(
            javabridge.call(
                self.jobject, "applyCostMatrix", "(Lweka/core/Instances;Ljava/util/Random;)Lweka/core/Instances;",
                data.jobject, rnd.jobject))

    def expected_costs(self, class_probs, inst=None):
        """
        Calculates the expected misclassification cost for each possible class value, given class probability
        estimates.

        :param class_probs: the class probabilities
        :type class_probs: ndarray
        :return: the calculated costs
        :rtype: ndarray
        """
        if inst is None:
            costs = javabridge.call(
                self.jobject, "expectedCosts", "([D)[D", javabridge.get_env().make_double_array(class_probs))
            return javabridge.get_env().get_double_array_elements(costs)
        else:
            costs = javabridge.call(
                self.jobject, "expectedCosts", "([DLweka/core/Instance;)[D",
                javabridge.get_env().make_double_array(class_probs), inst.jobject)
            return javabridge.get_env().get_double_array_elements(costs)

    def get_cell(self, row, col):
        """
        Returns the JB_Object at the specified location.

        :param row: the 0-based index of the row
        :type row: int
        :param col: the 0-based index of the column
        :type col: int
        :return: the object in that cell
        :rtype: JB_Object
        """
        return javabridge.call(
            self.jobject, "getCell", "(II)Ljava/lang/Object;", row, col)

    def set_cell(self, row, col, obj):
        """
        Sets the JB_Object at the specified location. Automatically unwraps JavaObject.

        :param row: the 0-based index of the row
        :type row: int
        :param col: the 0-based index of the column
        :type col: int
        :param obj: the object for that cell
        :type obj: object
        """
        if isinstance(obj, JavaObject):
            obj = obj.jobject
        javabridge.call(
            self.jobject, "setCell", "(IILjava/lang/Object;)V", row, col, obj)

    def get_element(self, row, col, inst=None):
        """
        Returns the value at the specified location.

        :param row: the 0-based index of the row
        :type row: int
        :param col: the 0-based index of the column
        :type col: int
        :param inst: the Instace
        :type inst: Instance
        :return: the value in that cell
        :rtype: float
        """
        if inst is None:
            return javabridge.call(
                self.jobject, "getElement", "(II)D", row, col)
        else:
            return javabridge.call(
                self.jobject, "getElement", "(IILweka/core/Instance;)D", row, col, inst.jobject)

    def set_element(self, row, col, value):
        """
        Sets the float value at the specified location.

        :param row: the 0-based index of the row
        :type row: int
        :param col: the 0-based index of the column
        :type col: int
        :param value: the float value for that cell
        :type value: float
        """
        javabridge.call(
            self.jobject, "setElement", "(IID)V", row, col, value)

    def get_max_cost(self, class_value, inst=None):
        """
        Gets the maximum cost for a particular class value.

        :param class_value: the class value to get the maximum cost for
        :type class_value: int
        :param inst: the Instance
        :type inst: Instance
        :return: the cost
        :rtype: float
        """
        if inst is None:
            return javabridge.call(
                self.jobject, "getMaxCost", "(I)D", class_value)
        else:
            return javabridge.call(
                self.jobject, "getElement", "(ILweka/core/Instance;)D", class_value, inst.jobject)

    def initialize(self):
        """
        Initializes the matrix.
        """
        javabridge.call(self.jobject, "initialize", "()V")

    def normalize(self):
        """
        Normalizes the matrix.
        """
        javabridge.call(self.jobject, "normalize", "()V")

    @property
    def num_columns(self):
        """
        Returns the number of columns.

        :return: the number of columns
        :rtype: int
        """
        return javabridge.call(self.jobject, "numColumns", "()I")

    @property
    def num_rows(self):
        """
        Returns the number of rows.

        :return: the number of rows
        :rtype: int
        """
        return javabridge.call(self.jobject, "numRows", "()I")

    @property
    def size(self):
        """
        Returns the number of rows/columns.

        :return: the number of rows/columns
        :rtype: int
        """
        return javabridge.call(self.jobject, "size", "()I")

    def to_matlab(self):
        """
        Returns the matrix in Matlab format.

        :return: the matrix as Matlab formatted string
        :rtype: str
        """
        return javabridge.call(self.jobject, "toMatlab", "()Ljava/lang/String;")

    @classmethod
    def parse_matlab(cls, matlab):
        """
        Parses the costmatrix definition in matlab format and returns a matrix.

        :param matlab: the matlab matrix string, eg [1 2; 3 4].
        :type matlab: str
        :return: the generated matrix
        :rtype: CostMatrix
        """
        return CostMatrix(
            matrx=javabridge.static_call(
                "weka/classifiers/CostMatrix", "parseMatlab",
                "(Ljava/lang/String;)Lweka/classifiers/CostMatrix;", matlab))


class Evaluation(JavaObject):
    """
    Evaluation class for classifiers.
    """

    def __init__(self, data, cost_matrix=None):
        """
        Initializes an Evaluation object.

        :param data: the data to use to initialize the priors with
        :type data: Instances
        :param cost_matrix: the cost matrix to use for initializing
        :type cost_matrix: CostMatrix
        """
        if cost_matrix is None:
            jobject = javabridge.make_instance(
                "weka/classifiers/EvaluationWrapper", "(Lweka/core/Instances;)V",
                data.jobject)
        else:
            jobject = javabridge.make_instance(
                "weka/classifiers/EvaluationWrapper", "(Lweka/core/Instances;Lweka/classifiers/CostMatrix;)V",
                data.jobject, cost_matrix.jobject)
        self.wrapper = jobject
        jobject = javabridge.call(jobject, "getEvaluation", "()Lweka/classifiers/Evaluation;")
        super(Evaluation, self).__init__(jobject)

    def crossvalidate_model(self, classifier, data, num_folds, rnd, output=None):
        """
        Crossvalidates the model using the specified data, number of folds and random number generator wrapper.

        :param classifier: the classifier to cross-validate
        :type classifier: Classifier
        :param data: the data to evaluate on
        :type data: Instances
        :param num_folds: the number of folds
        :type num_folds: int
        :param rnd: the random number generator to use
        :type rnd: Random
        :param output: the output generator to use
        :type output: PredictionOutput
        """
        if output is None:
            generator = []
        else:
            generator = [output.jobject]
        javabridge.call(
            self.jobject, "crossValidateModel",
            "(Lweka/classifiers/Classifier;Lweka/core/Instances;ILjava/util/Random;[Ljava/lang/Object;)V",
            classifier.jobject, data.jobject, num_folds, rnd.jobject, generator)

    def evaluate_train_test_split(self, classifier, data, percentage, rnd=None, output=None):
        """
        Splits the data into train and test, builds the classifier with the training data and
        evaluates it against the test set.

        :param classifier: the classifier to cross-validate
        :type classifier: Classifier
        :param data: the data to evaluate on
        :type data: Instances
        :param percentage: the percentage split to use (amount to use for training)
        :type percentage: double
        :param rnd: the random number generator to use, if None the order gets preserved
        :type rnd: Random
        :param output: the output generator to use
        :type output: PredictionOutput
        """
        train_inst, test_inst = data.train_test_split(percentage, rnd=rnd)
        cls = Classifier.make_copy(classifier)
        cls.build_classifier(train_inst)
        self.test_model(cls, test_inst, output=output)

    def test_model(self, classifier, data, output=None):
        """
        Evaluates the built model using the specified test data and returns the classifications.

        :param classifier: the trained classifier to evaluate
        :type classifier: Classifier
        :param data: the data to evaluate on
        :type data: Instances
        :param output: the output generator to use
        :type output: PredictionOutput
        :return: the classifications
        :rtype: ndarray
        """
        if output is None:
            generator = []
        else:
            output.header = data
            generator = [output.jobject]
        cls = javabridge.call(
            self.jobject, "evaluateModel",
            "(Lweka/classifiers/Classifier;Lweka/core/Instances;[Ljava/lang/Object;)[D",
            classifier.jobject, data.jobject, generator)
        if cls is None:
            return None
        else:
            return javabridge.get_env().get_double_array_elements(cls)

    def test_model_once(self, classifier, inst):
        """
        Evaluates the built model using the specified test instance and returns the classification.

        :param classifier: the classifier to cross-validate
        :type classifier: Classifier
        :param inst: the Instance to evaluate on
        :type inst: Instances
        :return: the classification
        :rtype: float
        """
        return javabridge.call(
            self.jobject, "evaluateModelOnce",
            "(Lweka/classifiers/Classifier;Lweka/core/Instance;)D",
            classifier.jobject, inst.jobject)

    def summary(self, title=None, complexity=False):
        """
        Generates a summary.

        :param title: optional title
        :type title: str
        :param complexity: whether to print the complexity information as well
        :type complexity: bool
        :return: the summary
        :rtype: str
        """
        if title is None:
            return javabridge.call(
                self.jobject, "toSummaryString", "()Ljava/lang/String;")
        else:
            return javabridge.call(
                self.jobject, "toSummaryString", "(Ljava/lang/String;Z)Ljava/lang/String;", title, complexity)

    def class_details(self, title=None):
        """
        Generates the class details.

        :param title: optional title
        :type title: str
        :return: the details
        :rtype: str
        """
        if title is None:
            return javabridge.call(
                self.jobject, "toClassDetailsString", "()Ljava/lang/String;")
        else:
            return javabridge.call(
                self.jobject, "toClassDetailsString", "(Ljava/lang/String;)Ljava/lang/String;", title)

    def matrix(self, title=None):
        """
        Generates the confusion matrix.

        :param title: optional title
        :type title: str
        :return: the matrix
        :rtype: str
        """
        if title is None:
            return javabridge.call(self.jobject, "toMatrixString", "()Ljava/lang/String;")
        else:
            return javabridge.call(self.jobject, "toMatrixString", "(Ljava/lang/String;)Ljava/lang/String;", title)

    def cumulative_margin_distribution(self):
        """
        Output the cumulative margin distribution as a string suitable for input for gnuplot or similar package.

        :return: the cumulative margin distribution
        :rtype: str
        """
        return javabridge.call(self.jobject, "toCumulativeMarginDistributionString", "()Ljava/lang/String;")

    def area_under_prc(self, class_index):
        """
        Returns the area under precision recall curve.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the area
        :rtype: float
        """
        return javabridge.call(self.jobject, "areaUnderPRC", "(I)D", class_index)

    @property
    def weighted_area_under_prc(self):
        """
        Returns the weighted area under precision recall curve.

        :return: the weighted area
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedAreaUnderPRC", "()D")

    def area_under_roc(self, class_index):
        """
        Returns the area under receiver operators characteristics curve.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the area
        :rtype: float
        """
        return javabridge.call(self.jobject, "areaUnderROC", "(I)D", class_index)

    @property
    def weighted_area_under_roc(self):
        """
        Returns the weighted area under receiver operator characteristic curve.

        :return: the weighted area
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedAreaUnderROC", "()D")

    @property
    def avg_cost(self):
        """
        Returns the average cost.

        :return: the cost
        :rtype: float
        """
        return javabridge.call(self.jobject, "avgCost", "()D")

    @property
    def total_cost(self):
        """
        Returns the total cost.

        :return: the cost
        :rtype: float
        """
        return javabridge.call(self.jobject, "totalCost", "()D")

    @property
    def confusion_matrix(self):
        """
        Returns the confusion matrix.

        :return: the matrix
        :rtype: ndarray
        """
        return typeconv.jdouble_matrix_to_ndarray(javabridge.call(self.jobject, "confusionMatrix", "()[[D"))

    @property
    def correct(self):
        """
        Returns the correct count (nominal classes).

        :return: the count
        :rtype: float
        """
        return javabridge.call(self.jobject, "correct", "()D")

    @property
    def incorrect(self):
        """
        Returns the incorrect count (nominal classes).

        :return: the count
        :rtype: float
        """
        return javabridge.call(self.jobject, "incorrect", "()D")

    @property
    def unclassified(self):
        """
        Returns the unclassified count.

        :return: the count
        :rtype: float
        """
        return javabridge.call(self.jobject, "unclassified", "()D")

    @property
    def num_instances(self):
        """
        Returns the number of instances that had a known class value.

        :return: the number of instances
        :rtype: float
        """
        return javabridge.call(self.jobject, "numInstances", "()D")

    @property
    def percent_correct(self):
        """
        Returns the percent correct (nominal classes).

        :return: the percentage
        :rtype: float
        """
        return javabridge.call(self.jobject, "pctCorrect", "()D")

    @property
    def percent_incorrect(self):
        """
        Returns the percent incorrect (nominal classes).

        :return: the percentage
        :rtype: float
        """
        return javabridge.call(self.jobject, "pctIncorrect", "()D")

    @property
    def percent_unclassified(self):
        """
        Returns the percent unclassified.

        :return: the percentage
        :rtype: float
        """
        return javabridge.call(self.jobject, "pctUnclassified", "()D")

    @property
    def correlation_coefficient(self):
        """
        Returns the correlation coefficient (numeric classes).

        :return: the coefficient
        :rtype: float
        """
        return javabridge.call(self.jobject, "correlationCoefficient", "()D")

    def matthews_correlation_coefficient(self, class_index):
        """
        Returns the Matthews correlation coefficient (nominal classes).

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the coefficient
        :rtype: float
        """
        return javabridge.call(self.jobject, "matthewsCorrelationCoefficient", "(I)D", class_index)

    @property
    def weighted_matthews_correlation(self):
        """
        Returns the weighted Matthews correlation (nominal classes).

        :return: the correlation
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedMatthewsCorrelation", "()D")

    @property
    def coverage_of_test_cases_by_predicted_regions(self):
        """
        Returns the coverage of the test cases by the predicted regions at the confidence level
        specified when evaluation was performed.

        :return: the coverage
        :rtype: float
        """
        return javabridge.call(self.jobject, "coverageOfTestCasesByPredictedRegions", "()D")

    @property
    def size_of_predicted_regions(self):
        """
        Returns  the average size of the predicted regions, relative to the range of the target in the
        training data, at the confidence level specified when evaluation was performed.

        :return:the size of the regions
        :rtype: float
        """
        return javabridge.call(self.jobject, "sizeOfPredictedRegions", "()D")

    @property
    def error_rate(self):
        """
        Returns the error rate (numeric classes).

        :return: the rate
        :rtype: float
        """
        return javabridge.call(self.jobject, "errorRate", "()D")

    @property
    def mean_absolute_error(self):
        """
        Returns the mean absolute error.

        :return: the error
        :rtype: float
        """
        return javabridge.call(self.jobject, "meanAbsoluteError", "()D")

    @property
    def relative_absolute_error(self):
        """
        Returns the relative absolute error.

        :return: the error
        :rtype: float
        """
        return javabridge.call(self.jobject, "relativeAbsoluteError", "()D")

    @property
    def root_mean_squared_error(self):
        """
        Returns the root mean squared error.

        :return: the error
        :rtype: float
        """
        return javabridge.call(self.jobject, "rootMeanSquaredError", "()D")

    @property
    def root_relative_squared_error(self):
        """
        Returns the root relative squared error.

        :return: the error
        :rtype: float
        """
        return javabridge.call(self.jobject, "rootRelativeSquaredError", "()D")

    @property
    def root_mean_prior_squared_error(self):
        """
        Returns the root mean prior squared error.

        :return: the error
        :rtype: float
        """
        return javabridge.call(self.jobject, "rootMeanPriorSquaredError", "()D")

    @property
    def mean_prior_absolute_error(self):
        """
        Returns the mean prior absolute error.

        :return: the error
        :rtype: float
        """
        return javabridge.call(self.jobject, "meanPriorAbsoluteError", "()D")

    def false_negative_rate(self, class_index):
        """
        Returns the false negative rate.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the rate
        :rtype: float
        """
        return javabridge.call(self.jobject, "falseNegativeRate", "(I)D", class_index)

    @property
    def weighted_false_negative_rate(self):
        """
        Returns the weighted false negative rate.

        :return: the rate
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedFalseNegativeRate", "()D")

    def false_positive_rate(self, class_index):
        """
        Returns the false positive rate.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the rate
        :rtype: float
        """
        return javabridge.call(self.jobject, "falsePositiveRate", "(I)D", class_index)

    @property
    def weighted_false_positive_rate(self):
        """
        Returns the weighted false positive rate.

        :return: the rate
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedFalsePositiveRate", "()D")

    def num_false_negatives(self, class_index):
        """
        Returns the number of false negatives.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the count
        :rtype: float
        """
        return javabridge.call(self.jobject, "numFalseNegatives", "(I)D", class_index)

    def true_negative_rate(self, class_index):
        """
        Returns the true negative rate.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the rate
        :rtype: float
        """
        return javabridge.call(self.jobject, "trueNegativeRate", "(I)D", class_index)

    @property
    def weighted_true_negative_rate(self):
        """
        Returns the weighted true negative rate.

        :return: the rate
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedTrueNegativeRate", "()D")

    def num_true_negatives(self, class_index):
        """
        Returns the number of true negatives.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the count
        :rtype: float
        """
        return javabridge.call(self.jobject, "numTrueNegatives", "(I)D", class_index)

    def num_false_positives(self, class_index):
        """
        Returns the number of false positives.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the count
        :rtype: float
        """
        return javabridge.call(self.jobject, "numFalsePositives", "(I)D", class_index)

    def true_positive_rate(self, class_index):
        """
        Returns the true positive rate.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the rate
        :rtype: float
        """
        return javabridge.call(self.jobject, "truePositiveRate", "(I)D", class_index)

    @property
    def weighted_true_positive_rate(self):
        """
        Returns the weighted true positive rate.

        :return: the rate
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedTruePositiveRate", "()D")

    def num_true_positives(self, class_index):
        """
        Returns the number of true positives.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the count
        :rtype: float
        """
        return javabridge.call(self.jobject, "numTruePositives", "(I)D", class_index)

    def f_measure(self, class_index):
        """
        Returns the f measure.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the measure
        :rtype: float
        """
        return javabridge.call(self.jobject, "fMeasure", "(I)D", class_index)

    @property
    def weighted_f_measure(self):
        """
        Returns the weighted f measure.

        :return: the measure
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedFMeasure", "()D")

    @property
    def unweighted_macro_f_measure(self):
        """
        Returns the unweighted macro-averaged F-measure.

        :return: the measure
        :rtype: float
        """
        return javabridge.call(self.jobject, "unweightedMacroFmeasure", "()D")

    @property
    def unweighted_micro_f_measure(self):
        """
        Returns the unweighted micro-averaged F-measure.

        :return: the measure
        :rtype: float
        """
        return javabridge.call(self.jobject, "unweightedMicroFmeasure", "()D")

    def precision(self, class_index):
        """
        Returns the precision.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the precision
        :rtype: float
        """
        return javabridge.call(self.jobject, "precision", "(I)D", class_index)

    @property
    def weighted_precision(self):
        """
        Returns the weighted precision.

        :return: the precision
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedPrecision", "()D")

    def recall(self, class_index):
        """
        Returns the recall.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the recall
        :rtype: float
        """
        return javabridge.call(self.jobject, "recall", "(I)D", class_index)

    @property
    def weighted_recall(self):
        """
        Returns the weighted recall.

        :return: the recall
        :rtype: float
        """
        return javabridge.call(self.jobject, "weightedRecall", "()D")

    @property
    def kappa(self):
        """
        Returns kappa.

        :return: kappa
        :rtype: float
        """
        return javabridge.call(self.jobject, "kappa", "()D")

    @property
    def kb_information(self):
        """
        Returns KB information.

        :return: the information
        :rtype: float
        """
        return javabridge.call(self.jobject, "KBInformation", "()D")

    @property
    def kb_mean_information(self):
        """
        Returns KB mean information.

        :return: the information
        :rtype: float
        """
        return javabridge.call(self.jobject, "KBMeanInformation", "()D")

    @property
    def kb_relative_information(self):
        """
        Returns KB relative information.

        :return: the information
        :rtype: float
        """
        return javabridge.call(self.jobject, "KBRelativeInformation", "()D")

    @property
    def sf_entropy_gain(self):
        """
        Returns the total SF, which is the null model entropy minus the scheme entropy.

        :return: the gain
        :rtype: float
        """
        return javabridge.call(self.jobject, "SFEntropyGain", "()D")

    @property
    def sf_mean_entropy_gain(self):
        """
        Returns the SF per instance, which is the null model entropy minus the scheme entropy, per instance.

        :return: the gain
        :rtype: float
        """
        return javabridge.call(self.jobject, "SFMeanEntropyGain", "()D")

    @property
    def sf_mean_prior_entropy(self):
        """
        Returns the entropy per instance for the null model.

        :return: the entropy
        :rtype: float
        """
        return javabridge.call(self.jobject, "SFMeanPriorEntropy", "()D")

    @property
    def sf_mean_scheme_entropy(self):
        """
        Returns the entropy per instance for the scheme.

        :return: the entropy
        :rtype: float
        """
        return javabridge.call(self.jobject, "SFMeanSchemeEntropy", "()D")

    @property
    def sf_prior_entropy(self):
        """
        Returns the total entropy for the null model.

        :return: the entropy
        :rtype: float
        """
        return javabridge.call(self.jobject, "SFPriorEntropy", "()D")

    @property
    def sf_scheme_entropy(self):
        """
        Returns the total entropy for the scheme.

        :return: the entropy
        :rtype: float
        """
        return javabridge.call(self.jobject, "SFchemeEntropy", "()D")

    @property
    def class_priors(self):
        """
        Returns the class priors.

        :return: the priors
        :rtype: ndarray
        """
        return javabridge.get_env().get_double_array_elements(javabridge.call(self.jobject, "getClassPriors", "()[D"))

    @class_priors.setter
    def class_priors(self, data):
        """
        Sets the class priors derived from the dataset.

        :param data: the dataset to derive the priors from
        :type data: Instances
        """
        javabridge.call(self.jobject, "setClassPriors", "(Lweka/core/Instances;)V", data)

    @property
    def header(self):
        """
        Returns the header format.

        :return: the header format
        :rtype: Instances
        """
        return Instances(javabridge.call(self.jobject, "getHeader", "()Lweka/core/Instances;"))

    @property
    def discard_predictions(self):
        """
        Returns whether to discard predictions (saves memory).

        :return: True if to discard
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getDiscardPredictions", "()Z")

    @discard_predictions.setter
    def discard_predictions(self, discard):
        """
        Sets whether to discard predictions (saves memory).

        :param discard: True if to discard predictions
        :type discard: bool
        """
        javabridge.call(self.jobject, "setDiscardPredictions", "(Z)V", discard)

    @property
    def predictions(self):
        """
        Returns the predictions.

        :return: the predictions. None if not available
        :rtype: list
        """
        preds = javabridge.get_collection_wrapper(
            javabridge.call(self.jobject, "predictions", "()Ljava/util/ArrayList;"))
        if self.discard_predictions:
            result = None
        else:
            result = []
            for pred in preds:
                if is_instance_of(pred, "weka.classifiers.evaluation.NominalPrediction"):
                    result.append(NominalPrediction(pred))
                elif is_instance_of(pred, "weka.classifiers.evaluation.NumericPrediction"):
                    result.append(NumericPrediction(pred))
                else:
                    result.append(Prediction(pred))
        return result

    @classmethod
    def evaluate_model(cls, classifier, args):
        """
        Evaluates the classifier with the given options.

        :param classifier: the classifier instance to use
        :type classifier: Classifier
        :param args: the command-line arguments to use
        :type args: list
        :return: the evaluation string
        :rtype: str
        """
        return javabridge.static_call(
            "Lweka/classifiers/Evaluation;", "evaluateModel",
            "(Lweka/classifiers/Classifier;[Ljava/lang/String;)Ljava/lang/String;",
            classifier.jobject, args)


class PredictionOutput(OptionHandler):
    """
    For collecting predictions and generating output from.
    Must be derived from weka.classifiers.evaluation.output.prediction.AbstractOutput
    """

    def __init__(self, classname="weka.classifiers.evaluation.output.prediction.PlainText", jobject=None, options=None):
        """
        Initializes the specified output generator using either the classname or the supplied JB_Object.

        :param classname: the classname of the generator
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = PredictionOutput.new_instance(classname)
        self.enforce_type(jobject, "weka.classifiers.evaluation.output.prediction.AbstractOutput")
        super(PredictionOutput, self).__init__(jobject=jobject, options=options)
        buf = javabridge.make_instance("java/lang/StringBuffer", "()V")
        javabridge.call(self.jobject, "setBuffer", "(Ljava/lang/StringBuffer;)V", buf)

    @property
    def header(self):
        """
        Returns the header format.

        :return: The dataset format
        :rtype: Instances
        """
        return Instances(javabridge.call(self.jobject, "getHeader", "()Lweka/core/Instances;"))

    @header.setter
    def header(self, data):
        """
        Sets the header format.

        :param data: The dataset format
        :type data: Instances
        """
        javabridge.call(self.jobject, "setHeader", "(Lweka/core/Instances;)V", data.jobject)

    def print_header(self):
        """
        Prints the header to the buffer.
        """
        javabridge.call(self.jobject, "printHeader", "()V")

    def print_footer(self):
        """
        Prints the footer to the buffer.
        """
        javabridge.call(self.jobject, "printFooter", "()V")

    def print_all(self, cls, data):
        """
        Prints the header, classifications and footer to the buffer.

        :param cls: the classifier
        :type cls: Classifier
        :param data: the test data
        :type data: Instances
        """
        javabridge.call(
            self.jobject, "print", "(Lweka/classifiers/Classifier;Lweka/core/Instances;)V",
            cls.jobject, data.jobject)

    def print_classifications(self, cls, data):
        """
        Prints the classifications to the buffer.

        :param cls: the classifier
        :type cls: Classifier
        :param data: the test data
        :type data: Instances
        """
        javabridge.call(
            self.jobject, "printClassifications", "(Lweka/classifiers/Classifier;Lweka/core/Instances;)V",
            cls.jobject, data.jobject)

    def print_classification(self, cls, inst, index):
        """
        Prints the classification to the buffer.

        :param cls: the classifier
        :type cls: Classifier
        :param inst: the test instance
        :type inst: Instance
        :param index: the 0-based index of the test instance
        :type index: int
        """
        javabridge.call(
            self.jobject, "printClassification", "(Lweka/classifiers/Classifier;Lweka/core/Instance;I)V",
            cls.jobject, inst.jobject, index)

    def buffer_content(self):
        """
        Returns the content of the buffer as string.

        :return: The buffer content
        :rtype: str
        """
        return javabridge.to_string(javabridge.call(self.jobject, "getBuffer", "()Ljava/lang/StringBuffer;"))

    def __str__(self):
        """
        Returns the content of the buffer.

        :return: the current buffer content
        :rtype: str
        """
        return self.buffer_content()


def predictions_to_instances(data, preds):
    """
    Turns the predictions turned into an Instances object.

    :param data: the original dataset format
    :type data: Instances
    :param preds: the predictions to convert
    :type preds: list
    :return: the predictions, None if no predictions present
    :rtype: Instances
    """
    if len(preds) == 0:
        return None

    is_numeric = isinstance(preds[0], NumericPrediction)

    # create header
    atts = []
    if is_numeric:
        atts.append(Attribute.create_numeric("index"))
        atts.append(Attribute.create_numeric("weight"))
        atts.append(Attribute.create_numeric("actual"))
        atts.append(Attribute.create_numeric("predicted"))
        atts.append(Attribute.create_numeric("error"))
    else:
        atts.append(Attribute.create_numeric("index"))
        atts.append(Attribute.create_numeric("weight"))
        atts.append(data.class_attribute.copy(name="actual"))
        atts.append(data.class_attribute.copy(name="predicted"))
        atts.append(Attribute.create_nominal("error", ["no", "yes"]))
        atts.append(Attribute.create_numeric("classification"))
        for i in range(data.class_attribute.num_values):
            atts.append(Attribute.create_numeric("distribution-" + data.class_attribute.value(i)))

    result = Instances.create_instances("Predictions", atts, len(preds))

    count = 0
    for pred in preds:
        count += 1
        if is_numeric:
            values = array([count, pred.weight, pred.actual, pred.predicted, pred.error])
        else:
            if pred.actual == pred.predicted:
                error = 0.0
            else:
                error = 1.0
            l = [count, pred.weight, pred.actual, pred.predicted, error, max(pred.distribution)]
            for i in range(data.class_attribute.num_values):
                l.append(pred.distribution[i])
            values = array(l)
        inst = Instance.create_instance(values)
        result.add_instance(inst)

    return result


def main(args=None):
    """
    Runs a classifier from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Performs classification/regression from the command-line. Calls JVM start/stop automatically.')
    parser.add_argument("-j", metavar="classpath", dest="classpath", help="additional classpath, jars/directories")
    parser.add_argument("-X", metavar="heap", dest="heap", help="max heap size for jvm, e.g., 512m")
    parser.add_argument("-t", metavar="train", dest="train", required=True, help="Training set file")
    parser.add_argument("-T", metavar="test", dest="test", help="Test set file")
    parser.add_argument("-c", metavar="class index", dest="classindex", help="1-based class attribute index")
    parser.add_argument("-d", metavar="outmodel", dest="outmodel", help="model output file name")
    parser.add_argument("-l", metavar="inmodel", dest="inmodel", help="model input file name")
    parser.add_argument("-x", metavar="num folds", dest="numfolds", help="number of folds for cross-validation")
    parser.add_argument("-s", metavar="seed", dest="seed", help="seed value for randomization")
    parser.add_argument("-v", action="store_true", dest="notrainstats", help="no statistics for training")
    parser.add_argument("-o", action="store_true", dest="onlystats", help="only statistics, don't output model")
    parser.add_argument("-i", action="store_true", dest="irstats", help="output information retrieval statistics")
    parser.add_argument("-k", action="store_true", dest="itstats", help="output information theoretic statistics")
    parser.add_argument("-m", metavar="costmatrix", dest="costmatrix", help="cost matrix file")
    parser.add_argument("-g", metavar="graph", dest="graph", help="output file for graph (if supported)")
    parser.add_argument("classifier", help="classifier classname, e.g., weka.classifiers.trees.J48")
    parser.add_argument("option", nargs=argparse.REMAINDER, help="additional classifier options")
    parsed = parser.parse_args(args=args)
    jars = []
    if parsed.classpath is not None:
        jars = parsed.classpath.split(os.pathsep)
    params = []
    if parsed.train is not None:
        params.extend(["-t", parsed.train])
    if parsed.test is not None:
        params.extend(["-T", parsed.test])
    if parsed.classindex is not None:
        params.extend(["-c", parsed.classindex])
    if parsed.outmodel is not None:
        params.extend(["-d", parsed.outmodel])
    if parsed.inmodel is not None:
        params.extend(["-l", parsed.inmodel])
    if parsed.numfolds is not None:
        params.extend(["-x", parsed.numfolds])
    if parsed.seed is not None:
        params.extend(["-s", parsed.seed])
    if parsed.notrainstats:
        params.append("-v")
    if parsed.onlystats:
        params.append("-o")
    if parsed.irstats:
        params.append("-i")
    if parsed.itstats:
        params.append("-k")
    if parsed.costmatrix is not None:
        params.extend(["-m", parsed.costmatrix])
    if parsed.graph is not None:
        params.extend(["-g", parsed.graph])

    jvm.start(jars, max_heap_size=parsed.heap, packages=True)

    logger.debug("Commandline: " + join_options(sys.argv[1:]))

    try:
        classifier = Classifier(classname=parsed.classifier)
        if len(parsed.option) > 0:
            classifier.options = parsed.option
        print(Evaluation.evaluate_model(classifier, params))
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
