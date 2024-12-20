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
# Copyright (C) 2014-2024 Fracpete (pythonwekawrapper at gmail dot com)

import sys
import os
import logging
import argparse
import traceback
import weka.core.jvm as jvm
import weka.core.typeconv as typeconv
import weka.core.classes as classes
from jpype import JClass, JObject
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
logger.setLevel(logging.INFO)


class Classifier(OptionHandler):
    """
    Wrapper class for classifiers.
    """

    def __init__(self, classname="weka.classifiers.rules.ZeroR", jobject=None, options=None):
        """
        Initializes the specified classifier using either the classname or the supplied JPype object.

        :param classname: the classname of the classifier
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Classifier.new_instance(classname)
        self.enforce_type(jobject, "weka.classifiers.Classifier")
        self.is_updateable = self.check_type(jobject, "weka.classifiers.UpdateableClassifier")
        self.is_drawable = self.check_type(jobject, "weka.core.Drawable")
        self.is_additional_measure_producer = self.check_type(jobject, "weka.core.AdditionalMeasureProducer")
        self.is_batchpredictor = self.check_type(jobject, "weka.core.BatchPredictor")
        self._header = None
        super(Classifier, self).__init__(jobject=jobject, options=options)

    def _make_calls(self):
        """
        Method for obtaining method instances for faster access.
        Members must start with "_mc_"
        """
        super(Classifier, self)._make_calls()
        self._mc_classify = self.jobject.classifyInstance
        self._mc_distribution = self.jobject.distributionForInstance
        if self.is_batchpredictor:
            self._mc_distributions = self.jobject.distributionsForInstances

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

    def build_classifier(self, data):
        """
        Builds the classifier with the data.

        :param data: the data to train the classifier with
        :type data: Instances
        """
        self._header = data.copy_structure()
        self.jobject.buildClassifier(data.jobject)

    def update_classifier(self, inst):
        """
        Updates the classifier with the instance.

        :param inst: the Instance to update the classifier with
        :type inst: Instance
        """
        if self.is_updateable:
            self.jobject.updateClassifier(inst.jobject)
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
        return typeconv.jdouble_array_to_ndarray(self._mc_distribution(inst.jobject))

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
            return self.jobject.getBatchSize()
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
            self.jobject.setBatchSize(size)

    def has_efficient_batch_prediction(self):
        """
        Returns whether the classifier implements a more efficient batch prediction.

        :return: True if a more efficient batch prediction is implemented, always False if not batch predictor
        :rtype: bool
        """
        if self.is_batchpredictor:
            return self.jobject.implementsMoreEfficientBatchPrediction()
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
            return self.jobject.graphType()
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
            return self.jobject.graph()
        else:
            return None

    @property
    def additional_measures(self):
        """
        Returns the list of additional measures if implementing weka.core.AdditionalMeasureProducer, otherwise None.

        :return: the additional measures
        :rtype: str
        """
        if self.is_additional_measure_producer:
            enm = self.jobject.enumerateMeasures()
            if enm is None:
                return None
            else:
                return typeconv.jenumeration_to_list(enm)
        else:
            return None

    def additional_measure(self, measure):
        """
        Returns the specified additional measure if implementing weka.core.AdditionalMeasureProducer, otherwise None.

        :param measure: the measure to retrieve
        :type measure: str
        :return: the additional measure
        :rtype: str
        """
        if self.is_additional_measure_producer:
            return self.jobject.getMeasure(measure)
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
        return self.jobject.toSource(classname)

    @classmethod
    def make_copy(cls, classifier):
        """
        Creates a copy of the classifier.

        :param classifier: the classifier to copy
        :type classifier: Classifier
        :return: the copy of the classifier
        :rtype: Classifier
        """
        return Classifier(jobject=JClass("weka.classifiers.AbstractClassifier").makeCopy(classifier.jobject))

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
        Initializes the specified classifier using either the classname or the supplied JPype object.

        :param classname: the classname of the classifier
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        return Classifier(jobject=self.jobject.getClassifier())

    @classifier.setter
    def classifier(self, classifier):
        """
        Sets the base classifier.

        :param classifier: the base classifier to use
        :type classifier: Classifier
        """
        self.jobject.setClassifier(classifier.jobject)


class FilteredClassifier(SingleClassifierEnhancer):
    """
    Wrapper class for the filtered classifier.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified classifier using its classname or the supplied JPype object.

        :param jobject: the JPype object to use
        :type jobject: JPype object
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

    def check_for_modified_class_attribute(self, check):
        """
        Sets whether to check for class attribute modifications.

        :param check: True if checking for modifications
        :type check: bool
        """
        self.jobject.setDoNotCheckForModifiedClassAttribute(not check)


class AttributeSelectedClassifier(SingleClassifierEnhancer):
    """
    Wrapper class for the AttributeSelectedClassifier.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified classifier using its classname or the supplied JPype object.

        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        return ASEvaluation(jobject=self.jobject.getEvaluator())

    @evaluator.setter
    def evaluator(self, evl):
        """
        Sets the evaluator.

        :param evl: the evaluator to use
        :type evl: ASEvaluation
        """
        self.jobject.setEvaluator(evl.jobject)

    @property
    def search(self):
        """
        Returns the search.

        :return: the search in use
        :rtype: ASSearch
        """
        return ASSearch(jobject=self.jobject.getSearch())

    @search.setter
    def search(self, search):
        """
        Sets the search.

        :param search: the search to use
        :type search: ASSearch
        """
        self.jobject.setSearch(search.jobject)


class GridSearch(SingleClassifierEnhancer):
    """
    Wrapper class for the GridSearch meta-classifier.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified classifier using its classname or the supplied JPype object.

        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        return SelectedTag(self.jobject.getEvaluation())

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
        self.jobject.setEvaluation(evl.jobject)

    @property
    def x(self):
        """
        Returns a dictionary with all the current values for the X of the grid.
        Keys for the dictionary: property, min, max, step, base, expression
        Types: property=str, min=float, max=float, step=float, base=float, expression=str

        :return: the dictionary with the parameters
        :rtype: dict
        """
        result = dict()
        result["property"] = self.jobject.getXProperty()
        result["min"] = self.jobject.getXMin()
        result["max"] = self.jobject.getXMax()
        result["step"] = self.jobject.getXStep()
        result["base"] = self.jobject.getXBase()
        result["expression"] = self.jobject.getXExpression()
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
            self.jobject.setXProperty(d["property"])
        if "min" in d:
            self.jobject.setXMin(d["min"])
        if "max" in d:
            self.jobject.setXMax(d["max"])
        if "step" in d:
            self.jobject.setXStep(d["step"])
        if "base" in d:
            self.jobject.setXBase(d["base"])
        if "expression" in d:
            self.jobject.setXExpression(d["expression"])

    @property
    def y(self):
        """
        Returns a dictionary with all the current values for the Y of the grid.
        Keys for the dictionary: property, min, max, step, base, expression
        Types: property=str, min=float, max=float, step=float, base=float, expression=str

        :return: the dictionary with the parameters
        :rtype: dict
        """
        result = dict()
        result["property"] = self.jobject.getYProperty()
        result["min"] = self.jobject.getYMin()
        result["max"] = self.jobject.getYMax()
        result["step"] = self.jobject.getYStep()
        result["base"] = self.jobject.getYBase()
        result["expression"] = self.jobject.getYExpression()
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
            self.jobject.setYProperty(d["property"])
        if "min" in d:
            self.jobject.setYMin(d["min"])
        if "max" in d:
            self.jobject.setYMax(d["max"])
        if "step" in d:
            self.jobject.setYStep(d["step"])
        if "base" in d:
            self.jobject.setYBase(d["base"])
        if "expression" in d:
            self.jobject.setYExpression(d["expression"])

    @property
    def best(self):
        """
        Returns the best classifier setup found during the th search.

        :return: the best classifier setup
        :rtype: Classifier
        """
        return Classifier(jobject=self.jobject.getBestClassifier())


class MultiSearch(SingleClassifierEnhancer):
    """
    Wrapper class for the MultiSearch meta-classifier.
    NB: 'multi-search-weka-package' must be installed (https://github.com/fracpete/multisearch-weka-package),
    version 2016.1.15 or later.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified classifier using its classname or the supplied JPype object.

        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        return SelectedTag(self.jobject.getEvaluation())

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
        self.jobject.setEvaluation(evl.jobject)

    @property
    def parameters(self):
        """
        Returns the list of currently set search parameters.

        :return: the list of AbstractSearchParameter objects
        :rtype: list
        """
        array = JavaArray(self.jobject.getSearchParameters())
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
        array = JavaArray(JavaArray.new_array("weka.core.setupgenerator.AbstractParameter", len(params)))
        for idx, obj in enumerate(params):
            array[idx] = obj.jobject
        self.jobject.setSearchParameters(array.jobject)

    @property
    def best(self):
        """
        Returns the best classifier setup found during the th search.

        :return: the best classifier setup
        :rtype: Classifier
        """
        return Classifier(jobject=self.jobject.getBestClassifier())


class MultipleClassifiersCombiner(Classifier):
    """
    Wrapper class for classifiers that use a multiple base classifiers.
    """

    def __init__(self, classname=None, jobject=None, options=None):
        """
        Initializes the specified classifier using either the classname or the supplied JPype object.

        :param classname: the classname of the classifier
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        result = []
        for obj in self.jobject.getClassifiers():
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
        self.jobject.setClassifiers(obj)

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
        Initializes the specified kernel using either the classname or the supplied JPype object.

        :param classname: the classname of the kernel
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        return Capabilities(self.jobject.getCapabilities())

    @property
    def checks_turned_off(self):
        """
        Returns whether checks are turned off.

        :return: True if checks turned off
        :rtype: bool
        """
        return self.jobject.getChecksTurnedOff()

    @checks_turned_off.setter
    def checks_turned_off(self, off):
        """
        Turns any checks on/off.

        :param off: True to turn off checks
        :type off: bool
        """
        self.jobject.setChecksTurnedOff(off)

    def clean(self):
        """
        Frees the memory used by the kernel.
        """
        self.jobject.clean()

    def build_kernel(self, data):
        """
        Builds the classifier with the data.

        :param data: the data to train the classifier with
        :type data: Instances
        """
        self.jobject.buildKernel(data.jobject)

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
        return self.jobject.eval(id1, id2, jinst1)

    @classmethod
    def make_copy(cls, kernel):
        """
        Creates a copy of the kernel.

        :param kernel: the kernel to copy
        :type kernel: Kernel
        :return: the copy of the kernel
        :rtype: Kernel
        """
        return Kernel(jobject=JClass("weka.classifiers.functions.supportVector.Kernel").makeCopy(kernel.jobject))


class KernelClassifier(Classifier):
    """
    Wrapper class for classifiers that have a kernel property, like SMO.
    """

    def __init__(self, classname=None, jobject=None, options=None):
        """
        Initializes the specified classifier using either the classname or the supplied JPype object.

        :param classname: the classname of the classifier
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: list of commandline options
        :type options: list
        """
        if jobject is None:
            jobject = Classifier.new_instance(classname)
        self.enforce_type(jobject, "weka.classifiers.Classifier")
        if not JClass("weka.classifiers.KernelHelper").hasKernelProperty(jobject):
            raise Exception("Does not handle a kernel: " + classes.get_classname(jobject))
        super(KernelClassifier, self).__init__(classname=classname, jobject=jobject, options=options)

    @property
    def kernel(self):
        """
        Returns the current kernel.

        :return: the kernel or None if none found
        :rtype: Kernel
        """
        result = JClass("weka.classifiers.KernelHelper").getKernel(self.jobject)
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
        result = JClass("weka.classifiers.KernelHelper").setKernel(self.jobject, kernel.jobject)
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
        :type jobject: JPype object
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
        return self.jobject.actual()

    @property
    def predicted(self):
        """
        Returns the predicted value.

        :return: the predicted value (internal representation)
        :rtype: float
        """
        return self.jobject.predicted()

    @property
    def weight(self):
        """
        Returns the weight.

        :return: the weight of the Instance that was used
        :rtype: float
        """
        return self.jobject.weight()


class NominalPrediction(Prediction):
    """
    Wrapper class for a nominal prediction.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the prediction to wrap
        :type jobject: JPype object
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
        return typeconv.jdouble_array_to_ndarray(self.jobject.distribution())

    @property
    def margin(self):
        """
        Returns the margin.

        :return: the margin
        :rtype: float
        """
        return self.jobject.margin()


class NumericPrediction(Prediction):
    """
    Wrapper class for a numeric prediction.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the prediction to wrap
        :type jobject: JPype object
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
        return self.jobject.error()

    @property
    def prediction_intervals(self):
        """
        Returns the prediction intervals.

        :return: the intervals
        :rtype: ndarray
        """
        return typeconv.jdouble_matrix_to_ndarray(self.jobject.predictionIntervals())


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
        :type matrx: CostMatrix or ndarray or JPype object
        :param num_classes: the number of classes
        :type num_classes: int
        """
        if matrx is not None:
            if isinstance(matrx, CostMatrix):
                jobject = JClass("weka.classifiers.CostMatrix")(matrx.jobject)
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
            elif isinstance(matrx, JObject):
                super(CostMatrix, self).__init__(matrx)
            else:
                raise Exception(
                    "Matrix must be either a CostMatrix or a 2-dimensional numpy array: " + str(type(matrx)))
        elif not num_classes is None:
            jobject = JClass("weka.classifiers.CostMatrix")(num_classes)
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
        return Instances(self.jobject.applyCostMatrix(data.jobject, rnd.jobject))

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
            costs = self.jobject.expectedCosts(typeconv.to_jdouble_array(class_probs))
            return typeconv.jdouble_array_to_ndarray(costs)
        else:
            costs = self.jobject.expectedCosts(typeconv.to_jdouble_array(class_probs), inst.jobject)
            return typeconv.jdouble_array_to_ndarray(costs)

    def get_cell(self, row, col):
        """
        Returns the JPype object at the specified location.

        :param row: the 0-based index of the row
        :type row: int
        :param col: the 0-based index of the column
        :type col: int
        :return: the object in that cell
        :rtype: JPype object
        """
        return self.jobject.getCell(row, col)

    def set_cell(self, row, col, obj):
        """
        Sets the JPype object at the specified location. Automatically unwraps JavaObject.

        :param row: the 0-based index of the row
        :type row: int
        :param col: the 0-based index of the column
        :type col: int
        :param obj: the object for that cell
        :type obj: object
        """
        if isinstance(obj, JavaObject):
            obj = obj.jobject
        self.jobject.setCell(row, col, obj)

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
            return self.jobject.getElement(row, col)
        else:
            return self.jobject.getElement(row, col, inst.jobject)

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
        self.jobject.setElement(row, col, value)

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
            return self.jobject.getMaxCost(class_value)
        else:
            return self.jobject.getElement(class_value, inst.jobject)

    def initialize(self):
        """
        Initializes the matrix.
        """
        self.jobject.initialize()

    def normalize(self):
        """
        Normalizes the matrix.
        """
        self.jobject.normalize()

    @property
    def num_columns(self):
        """
        Returns the number of columns.

        :return: the number of columns
        :rtype: int
        """
        return self.jobject.numColumns()

    @property
    def num_rows(self):
        """
        Returns the number of rows.

        :return: the number of rows
        :rtype: int
        """
        return self.jobject.numRows()

    @property
    def size(self):
        """
        Returns the number of rows/columns.

        :return: the number of rows/columns
        :rtype: int
        """
        return self.jobject.size()

    def to_matlab(self):
        """
        Returns the matrix in Matlab format.

        :return: the matrix as Matlab formatted string
        :rtype: str
        """
        return self.jobject.toMatlab()

    @classmethod
    def parse_matlab(cls, matlab):
        """
        Parses the costmatrix definition in matlab format and returns a matrix.

        :param matlab: the matlab matrix string, eg [1 2; 3 4].
        :type matlab: str
        :return: the generated matrix
        :rtype: CostMatrix
        """
        return CostMatrix(matrx=JClass("weka.classifiers.CostMatrix").parseMatlab(matlab))


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
            jobject = JClass("weka.classifiers.EvaluationWrapper")(data.jobject)
        else:
            jobject = JClass("weka.classifiers.EvaluationWrapper")(data.jobject, cost_matrix.jobject)
        self.wrapper = jobject
        jobject = jobject.getEvaluation()
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
        self.jobject.crossValidateModel(classifier.jobject, data.jobject, num_folds, rnd.jobject, generator)

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
        cls = self.jobject.evaluateModel(classifier.jobject, data.jobject, generator)
        if cls is None:
            return None
        else:
            return typeconv.jdouble_array_to_ndarray(cls)

    def test_model_once(self, classifier, inst, store=False):
        """
        Evaluates the built model using the specified test instance and returns the classification.

        :param classifier: the classifier to cross-validate
        :type classifier: Classifier
        :param inst: the Instance to evaluate on
        :type inst: Instance
        :param store: whether to store the predictions (some statistics in class_details() like AUC require that)
        :type store: bool
        :return: the classification
        :rtype: float
        """
        if not store:
            return self.jobject.evaluateModelOnce(classifier.jobject, inst.jobject)
        else:
            return self.jobject.evaluateModelOnceAndRecordPrediction(classifier.jobject, inst.jobject)

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
            return self.jobject.toSummaryString()
        else:
            return self.jobject.toSummaryString(title, complexity)

    def class_details(self, title=None):
        """
        Generates the class details.

        :param title: optional title
        :type title: str
        :return: the details
        :rtype: str
        """
        if title is None:
            return self.jobject.toClassDetailsString()
        else:
            return self.jobject.toClassDetailsString(title)

    def matrix(self, title=None):
        """
        Generates the confusion matrix.

        :param title: optional title
        :type title: str
        :return: the matrix
        :rtype: str
        """
        if title is None:
            return self.jobject.toMatrixString()
        else:
            return self.jobject.toMatrixString(title)

    def cumulative_margin_distribution(self):
        """
        Output the cumulative margin distribution as a string suitable for input for gnuplot or similar package.

        :return: the cumulative margin distribution
        :rtype: str
        """
        return self.jobject.toCumulativeMarginDistributionString()

    def area_under_prc(self, class_index):
        """
        Returns the area under precision recall curve.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the area
        :rtype: float
        """
        return self.jobject.areaUnderPRC(class_index)

    @property
    def weighted_area_under_prc(self):
        """
        Returns the weighted area under precision recall curve.

        :return: the weighted area
        :rtype: float
        """
        return self.jobject.weightedAreaUnderPRC()

    def area_under_roc(self, class_index):
        """
        Returns the area under receiver operators characteristics curve.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the area
        :rtype: float
        """
        return self.jobject.areaUnderROC(class_index)

    @property
    def weighted_area_under_roc(self):
        """
        Returns the weighted area under receiver operator characteristic curve.

        :return: the weighted area
        :rtype: float
        """
        return self.jobject.weightedAreaUnderROC()

    @property
    def avg_cost(self):
        """
        Returns the average cost.

        :return: the cost
        :rtype: float
        """
        return self.jobject.avgCost()

    @property
    def total_cost(self):
        """
        Returns the total cost.

        :return: the cost
        :rtype: float
        """
        return self.jobject.totalCost()

    @property
    def confusion_matrix(self):
        """
        Returns the confusion matrix.

        :return: the matrix
        :rtype: ndarray
        """
        return typeconv.jdouble_matrix_to_ndarray(self.jobject.confusionMatrix())

    @property
    def correct(self):
        """
        Returns the correct count (nominal classes).

        :return: the count
        :rtype: float
        """
        return self.jobject.correct()

    @property
    def incorrect(self):
        """
        Returns the incorrect count (nominal classes).

        :return: the count
        :rtype: float
        """
        return self.jobject.incorrect()

    @property
    def unclassified(self):
        """
        Returns the unclassified count.

        :return: the count
        :rtype: float
        """
        return self.jobject.unclassified()

    @property
    def num_instances(self):
        """
        Returns the number of instances that had a known class value.

        :return: the number of instances
        :rtype: float
        """
        return self.jobject.numInstances()

    @property
    def percent_correct(self):
        """
        Returns the percent correct (nominal classes).

        :return: the percentage
        :rtype: float
        """
        return self.jobject.pctCorrect()

    @property
    def percent_incorrect(self):
        """
        Returns the percent incorrect (nominal classes).

        :return: the percentage
        :rtype: float
        """
        return self.jobject.pctIncorrect()

    @property
    def percent_unclassified(self):
        """
        Returns the percent unclassified.

        :return: the percentage
        :rtype: float
        """
        return self.jobject.pctUnclassified()

    @property
    def correlation_coefficient(self):
        """
        Returns the correlation coefficient (numeric classes).

        :return: the coefficient
        :rtype: float
        """
        return self.jobject.correlationCoefficient()

    def matthews_correlation_coefficient(self, class_index):
        """
        Returns the Matthews correlation coefficient (nominal classes).

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the coefficient
        :rtype: float
        """
        return self.jobject.matthewsCorrelationCoefficient(class_index)

    @property
    def weighted_matthews_correlation(self):
        """
        Returns the weighted Matthews correlation (nominal classes).

        :return: the correlation
        :rtype: float
        """
        return self.jobject.weightedMatthewsCorrelation()

    @property
    def coverage_of_test_cases_by_predicted_regions(self):
        """
        Returns the coverage of the test cases by the predicted regions at the confidence level
        specified when evaluation was performed.

        :return: the coverage
        :rtype: float
        """
        return self.jobject.coverageOfTestCasesByPredictedRegions()

    @property
    def size_of_predicted_regions(self):
        """
        Returns  the average size of the predicted regions, relative to the range of the target in the
        training data, at the confidence level specified when evaluation was performed.

        :return:the size of the regions
        :rtype: float
        """
        return self.jobject.sizeOfPredictedRegions()

    @property
    def error_rate(self):
        """
        Returns the error rate (numeric classes).

        :return: the rate
        :rtype: float
        """
        return self.jobject.errorRate()

    @property
    def mean_absolute_error(self):
        """
        Returns the mean absolute error.

        :return: the error
        :rtype: float
        """
        return self.jobject.meanAbsoluteError()

    @property
    def relative_absolute_error(self):
        """
        Returns the relative absolute error.

        :return: the error
        :rtype: float
        """
        return self.jobject.relativeAbsoluteError()

    @property
    def root_mean_squared_error(self):
        """
        Returns the root mean squared error.

        :return: the error
        :rtype: float
        """
        return self.jobject.rootMeanSquaredError()

    @property
    def root_relative_squared_error(self):
        """
        Returns the root relative squared error.

        :return: the error
        :rtype: float
        """
        return self.jobject.rootRelativeSquaredError()

    @property
    def root_mean_prior_squared_error(self):
        """
        Returns the root mean prior squared error.

        :return: the error
        :rtype: float
        """
        return self.jobject.rootMeanPriorSquaredError()

    @property
    def mean_prior_absolute_error(self):
        """
        Returns the mean prior absolute error.

        :return: the error
        :rtype: float
        """
        return self.jobject.meanPriorAbsoluteError()

    def false_negative_rate(self, class_index):
        """
        Returns the false negative rate.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the rate
        :rtype: float
        """
        return self.jobject.falseNegativeRate(class_index)

    @property
    def weighted_false_negative_rate(self):
        """
        Returns the weighted false negative rate.

        :return: the rate
        :rtype: float
        """
        return self.jobject.weightedFalseNegativeRate()

    def false_positive_rate(self, class_index):
        """
        Returns the false positive rate.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the rate
        :rtype: float
        """
        return self.jobject.falsePositiveRate(class_index)

    @property
    def weighted_false_positive_rate(self):
        """
        Returns the weighted false positive rate.

        :return: the rate
        :rtype: float
        """
        return self.jobject.weightedFalsePositiveRate()

    def num_false_negatives(self, class_index):
        """
        Returns the number of false negatives.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the count
        :rtype: float
        """
        return self.jobject.numFalseNegatives(class_index)

    def true_negative_rate(self, class_index):
        """
        Returns the true negative rate.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the rate
        :rtype: float
        """
        return self.jobject.trueNegativeRate(class_index)

    @property
    def weighted_true_negative_rate(self):
        """
        Returns the weighted true negative rate.

        :return: the rate
        :rtype: float
        """
        return self.jobject.weightedTrueNegativeRate()

    def num_true_negatives(self, class_index):
        """
        Returns the number of true negatives.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the count
        :rtype: float
        """
        return self.jobject.numTrueNegatives(class_index)

    def num_false_positives(self, class_index):
        """
        Returns the number of false positives.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the count
        :rtype: float
        """
        return self.jobject.numFalsePositives(class_index)

    def true_positive_rate(self, class_index):
        """
        Returns the true positive rate.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the rate
        :rtype: float
        """
        return self.jobject.truePositiveRate(class_index)

    @property
    def weighted_true_positive_rate(self):
        """
        Returns the weighted true positive rate.

        :return: the rate
        :rtype: float
        """
        return self.jobject.weightedTruePositiveRate()

    def num_true_positives(self, class_index):
        """
        Returns the number of true positives.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the count
        :rtype: float
        """
        return self.jobject.numTruePositives(class_index)

    def f_measure(self, class_index):
        """
        Returns the f measure.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the measure
        :rtype: float
        """
        return self.jobject.fMeasure(class_index)

    @property
    def weighted_f_measure(self):
        """
        Returns the weighted f measure.

        :return: the measure
        :rtype: float
        """
        return self.jobject.weightedFMeasure()

    @property
    def unweighted_macro_f_measure(self):
        """
        Returns the unweighted macro-averaged F-measure.

        :return: the measure
        :rtype: float
        """
        return self.jobject.unweightedMacroFmeasure()

    @property
    def unweighted_micro_f_measure(self):
        """
        Returns the unweighted micro-averaged F-measure.

        :return: the measure
        :rtype: float
        """
        return self.jobject.unweightedMicroFmeasure()

    def precision(self, class_index):
        """
        Returns the precision.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the precision
        :rtype: float
        """
        return self.jobject.precision(class_index)

    @property
    def weighted_precision(self):
        """
        Returns the weighted precision.

        :return: the precision
        :rtype: float
        """
        return self.jobject.weightedPrecision()

    def recall(self, class_index):
        """
        Returns the recall.

        :param class_index: the 0-based index of the class label
        :type class_index: int
        :return: the recall
        :rtype: float
        """
        return self.jobject.recall(class_index)

    @property
    def weighted_recall(self):
        """
        Returns the weighted recall.

        :return: the recall
        :rtype: float
        """
        return self.jobject.weightedRecall()

    @property
    def kappa(self):
        """
        Returns kappa.

        :return: kappa
        :rtype: float
        """
        return self.jobject.kappa()

    @property
    def kb_information(self):
        """
        Returns KB information.

        :return: the information
        :rtype: float
        """
        return self.jobject.KBInformation()

    @property
    def kb_mean_information(self):
        """
        Returns KB mean information.

        :return: the information
        :rtype: float
        """
        return self.jobject.KBMeanInformation()

    @property
    def kb_relative_information(self):
        """
        Returns KB relative information.

        :return: the information
        :rtype: float
        """
        return self.jobject.KBRelativeInformation()

    @property
    def sf_entropy_gain(self):
        """
        Returns the total SF, which is the null model entropy minus the scheme entropy.

        :return: the gain
        :rtype: float
        """
        return self.jobject.SFEntropyGain()

    @property
    def sf_mean_entropy_gain(self):
        """
        Returns the SF per instance, which is the null model entropy minus the scheme entropy, per instance.

        :return: the gain
        :rtype: float
        """
        return self.jobject.SFMeanEntropyGain()

    @property
    def sf_mean_prior_entropy(self):
        """
        Returns the entropy per instance for the null model.

        :return: the entropy
        :rtype: float
        """
        return self.jobject.SFMeanPriorEntropy()

    @property
    def sf_mean_scheme_entropy(self):
        """
        Returns the entropy per instance for the scheme.

        :return: the entropy
        :rtype: float
        """
        return self.jobject.SFMeanSchemeEntropy()

    @property
    def sf_prior_entropy(self):
        """
        Returns the total entropy for the null model.

        :return: the entropy
        :rtype: float
        """
        return self.jobject.SFPriorEntropy()

    @property
    def sf_scheme_entropy(self):
        """
        Returns the total entropy for the scheme.

        :return: the entropy
        :rtype: float
        """
        return self.jobject.SFchemeEntropy()

    @property
    def class_priors(self):
        """
        Returns the class priors.

        :return: the priors
        :rtype: ndarray
        """
        return typeconv.jdouble_array_to_ndarray(self.jobject.getClassPriors())

    @class_priors.setter
    def class_priors(self, data):
        """
        Sets the class priors derived from the dataset.

        :param data: the dataset to derive the priors from
        :type data: Instances
        """
        self.jobject.setClassPriors(data)

    @property
    def header(self):
        """
        Returns the header format.

        :return: the header format
        :rtype: Instances
        """
        return Instances(self.jobject.getHeader())

    @property
    def discard_predictions(self):
        """
        Returns whether to discard predictions (saves memory).

        :return: True if to discard
        :rtype: bool
        """
        return self.jobject.getDiscardPredictions()

    @discard_predictions.setter
    def discard_predictions(self, discard):
        """
        Sets whether to discard predictions (saves memory).

        :param discard: True if to discard predictions
        :type discard: bool
        """
        self.jobject.setDiscardPredictions(discard)

    @property
    def predictions(self):
        """
        Returns the predictions.

        :return: the predictions. None if not available
        :rtype: list
        """
        if self.discard_predictions:
            result = None
        else:
            result = []
            for pred in self.jobject.predictions():
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
        return JClass("weka.classifiers.Evaluation").evaluateModel(classifier.jobject, args)


class PredictionOutput(OptionHandler):
    """
    For collecting predictions and generating output from.
    Must be derived from weka.classifiers.evaluation.output.prediction.AbstractOutput
    """

    def __init__(self, classname="weka.classifiers.evaluation.output.prediction.PlainText", jobject=None, options=None):
        """
        Initializes the specified output generator using either the classname or the supplied JPype object.

        :param classname: the classname of the generator
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = PredictionOutput.new_instance(classname)
        self.enforce_type(jobject, "weka.classifiers.evaluation.output.prediction.AbstractOutput")
        super(PredictionOutput, self).__init__(jobject=jobject, options=options)
        self.jobject.setBuffer(JClass("java.lang.StringBuffer")())

    @property
    def header(self):
        """
        Returns the header format.

        :return: The dataset format
        :rtype: Instances
        """
        return Instances(self.jobject.getHeader())

    @header.setter
    def header(self, data):
        """
        Sets the header format.

        :param data: The dataset format
        :type data: Instances
        """
        self.jobject.setHeader(data.jobject)

    def print_header(self):
        """
        Prints the header to the buffer.
        """
        self.jobject.printHeader()

    def print_footer(self):
        """
        Prints the footer to the buffer.
        """
        self.jobject.printFooter()

    def print_all(self, cls, data):
        """
        Prints the header, classifications and footer to the buffer.

        :param cls: the classifier
        :type cls: Classifier
        :param data: the test data
        :type data: Instances
        """
        self.jobject.print_(cls.jobject, data.jobject)

    def print_classifications(self, cls, data):
        """
        Prints the classifications to the buffer.

        :param cls: the classifier
        :type cls: Classifier
        :param data: the test data
        :type data: Instances
        """
        self.jobject.printClassifications(cls.jobject, data.jobject)

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
        self.jobject.printClassification(cls.jobject, inst.jobject, index)

    def buffer_content(self):
        """
        Returns the content of the buffer as string.

        :return: The buffer content
        :rtype: str
        """
        return str(self.jobject.getBuffer())

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
        description='Performs classification/regression from the command-line. Calls JVM start/stop automatically.',
        prog='pww-classifier')
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

    logger.info("Commandline: " + join_options(sys.argv[1:]))

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
