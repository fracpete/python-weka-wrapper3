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

# dataset.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import numpy as np
from weka.core.classes import JavaObject
import weka.core.typeconv as typeconv

# logging setup
logger = logging.getLogger(__name__)


class Instances(JavaObject):
    """
    Wrapper class for weka.core.Instances.
    """
    
    def __init__(self, jobject):
        """
        Initializes the weka.core.Instances wrapper.

        :param jobject: the weka.core.Instances object to wrap
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.core.Instances")
        super(Instances, self).__init__(jobject)

    def _make_calls(self):
        """
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        super(Instances, self)._make_calls()
        self._mc_attribute = javabridge.make_call(self.jobject, "attribute", "(I)Lweka/core/Attribute;")
        self._mc_attribute_by_name = javabridge.make_call(self.jobject, "attribute", "(Ljava/lang/String;)Lweka/core/Attribute;")
        self._mc_num_attributes = javabridge.make_call(self.jobject, "numAttributes", "()I")
        self._mc_num_instances = javabridge.make_call(self.jobject, "numInstances", "()I")
        self._mc_get_class_index = javabridge.make_call(self.jobject, "classIndex", "()I")
        self._mc_set_class_index = javabridge.make_call(self.jobject, "setClassIndex", "(I)V")
        self._mc_class_attribute = javabridge.make_call(self.jobject, "classAttribute", "()Lweka/core/Attribute;")
        self._mc_get_instance = javabridge.make_call(self.jobject, "instance", "(I)Lweka/core/Instance;")
        self._mc_set_instance = javabridge.make_call(self.jobject, "set", "(ILweka/core/Instance;)Lweka/core/Instance;")
        self._mc_append_instance = javabridge.make_call(self.jobject, "add", "(Lweka/core/Instance;)Z")
        self._mc_insert_instance = javabridge.make_call(self.jobject, "add", "(ILweka/core/Instance;)V")

    def __iter__(self):
        """
        Allows iterating over the rows.

        :return: the iterator
        :rtype: InstanceIterator
        """
        return InstanceIterator(self)

    def __len__(self):
        """
        Returns the number of rows in the dataset.

        :return: the number of Instance objects
        :rtype: int
        """
        return self.num_instances

    @property
    def relationname(self):
        """
        Returns the name of the dataset.

        :return: the name
        :rtype: str
        """
        return javabridge.call(self.jobject, "relationName", "()Ljava/lang/String;")

    @relationname.setter
    def relationname(self, value):
        """
        Sets the name of the dataset.

        :param value: the name
        :type value: str
        """
        javabridge.call(self.jobject, "setRelationName", "(Ljava/lang/String;)V", value)

    @property
    def num_attributes(self):
        """
        Returns the number of attributes.

        :return: the number of attributes
        :rtype: int
        """
        return self._mc_num_attributes()

    def attributes(self):
        """
        Returns an iterator over the attributes.
        """
        return AttributeIterator(self)

    def attribute(self, index):
        """
        Returns the specified attribute.

        :param index: the 0-based index of the attribute
        :type index: int
        :return: the attribute
        :rtype: Attribute
        """
        return Attribute(self._mc_attribute(index))

    def attribute_names(self):
        """
        Returns a list of all the attribute names.

        :return: list of attribute names
        :rtype: list
        """
        result = []
        for i in range(self.num_attributes):
            result.append(self.attribute(i).name)
        return result

    def attribute_by_name(self, name):
        """
        Returns the specified attribute, None if not found.

        :param name: the name of the attribute
        :type name: str
        :return: the attribute or None
        :rtype: Attribute
        """
        att = self._mc_attribute_by_name(javabridge.get_env().new_string(name))
        if att is None:
            return None
        else:
            return Attribute(att)

    def attribute_stats(self, index):
        """
        Returns the specified attribute statistics.

        :param index: the 0-based index of the attribute
        :type index: int
        :return: the attribute statistics
        :rtype: AttributeStats
        """
        return AttributeStats(javabridge.call(self.jobject, "attributeStats", "(I)Lweka/core/AttributeStats;", index))

    def values(self, index):
        """
        Returns the internal values of this attribute from all the instance objects.

        :return: the values as numpy array
        :rtype: list
        """
        values = []
        for i in range(self.num_instances):
            inst = self.get_instance(i)
            values.append(inst.get_value(index))
        return np.array(values)

    @property
    def num_instances(self):
        """
        Returns the number of instances.

        :return: the number of instances
        :rtype: int
        """
        return self._mc_num_instances()

    @property
    def class_attribute(self):
        """
        Returns the currently set class attribute.

        :return: the class attribute
        :rtype: Attribute
        """
        return Attribute(self._mc_class_attribute())

    @property
    def class_index(self):
        """
        Returns the currently set class index (0-based).

        :return: the class index, -1 if not set
        :rtype: int
        """
        return self._mc_get_class_index()

    @class_index.setter
    def class_index(self, index):
        """
        Sets the class index (0-based).

        :param index: the new index, use -1 to unset
        :type index: int
        """
        self._mc_set_class_index(index)

    def has_class(self):
        """
        Returns whether a class attribute is set (convenience method).

        :return: whether a class attribute is currently set
        :rtype: bool
        """
        return self.class_index != -1

    def no_class(self):
        """
        Unsets the class attribute (convenience method).
        """
        self.class_index = -1

    def class_is_first(self):
        """
        Sets the first attribute as class attribute (convenience method).
        """
        self.class_index = 0

    def class_is_last(self):
        """
        Sets the last attribute as class attribute (convenience method).
        """
        self.class_index = self.num_attributes - 1

    def get_instance(self, index):
        """
        Returns the Instance object at the specified location.

        :param index: the 0-based index of the instance
        :type index: int
        :return: the instance
        :rtype: Instance
        """
        return Instance(self._mc_get_instance(index))

    def add_instance(self, inst, index=None):
        """
        Adds the specified instance to the dataset.

        :param inst: the Instance to add
        :type inst: Instance
        :param index: the 0-based index where to add the Instance
        :type index: int
        """
        if index is None:
            self._mc_append_instance(inst.jobject)
        else:
            self._mc_insert_instance(index, inst.jobject)

    def set_instance(self, index, inst):
        """
        Sets the Instance at the specified location in the dataset.

        :param index: the 0-based index of the instance to replace
        :type index: int
        :param inst: the Instance to set
        :type inst: Instance
        :return: the instance
        :rtype: Instance
        """
        return Instance(
            self._mc_set_instance(index, inst.jobject))
            
    def delete(self, index=None):
        """
        Removes either the specified Instance or all Instance objects.

        :param index: the 0-based index of the instance to remove
        :type index: int
        """
        if index is None:
            javabridge.call(self.jobject, "delete", "()V")
        else:
            javabridge.call(self.jobject, "delete", "(I)V", index)

    def delete_attribute(self, index):
        """
        Deletes an attribute at the given position.

        :param index: the 0-based index of the attribute to remove
        :type index: int
        """
        javabridge.call(self.jobject, "deleteAttributeAt", "(I)V", index)

    def delete_first_attribute(self):
        """
        Deletes the first attribute.
        """
        self.delete_attribute(0)

    def delete_last_attribute(self):
        """
        Deletes the last attribute.
        """
        self.delete_attribute(self.num_attributes - 1)

    def delete_attribute_type(self, typ):
        """
        Deletes all attributes of the given type in the dataset.

        :param typ: the attribute type to remove, see weka.core.Attribute Javadoc
        :type typ: int
        """
        javabridge.call(self.jobject, "deleteAttributeType", "(I)V", typ)

    def delete_with_missing(self, index):
        """
        Deletes all rows that have a missing value at the specified attribute index.

        :param index: the attribute index to check for missing attributes
        :type index: int
        """
        javabridge.call(self.jobject, "deleteWithMissing", "(I)V", index)

    def insert_attribute(self, att, index):
        """
        Inserts the attribute at the specified location.

        :param att: the attribute to insert
        :type att: Attribute
        :param index: the index to insert the attribute at
        :type index: int
        """
        javabridge.call(self.jobject, "insertAttributeAt", "(Lweka/core/Attribute;I)V", att.jobject, index)

    def compactify(self):
        """
        Compactifies the set of instances.
        """
        javabridge.call(self.jobject, "compactify", "()V")

    def sort(self, index):
        """
        Sorts the dataset using the specified attribute index.

        :param index: the index of the attribute
        :type index: int
        """
        javabridge.call(self.jobject, "sort", "(I)V", index)

    def randomize(self, random):
        """
        Randomizes the dataset using the random number generator.

        :param random: the random number generator to use
        :type random: Random
        """
        javabridge.call(self.jobject, "randomize", "(Ljava/util/Random;)V", random.jobject)

    def stratify(self, folds):
        """
        Stratifies the data after randomization for nominal class attributes.

        :param folds: the number of folds to perform the stratification for
        :type folds: int
        """
        javabridge.call(self.jobject, "stratify", "(I)V", folds)

    def train_cv(self, num_folds, fold, random=None):
        """
        Generates a training fold for cross-validation.

        :param num_folds: the number of folds of cross-validation, eg 10
        :type num_folds: int
        :param fold: the current fold (0-based)
        :type fold: int
        :param random: the random number generator
        :type random: Random
        :return: the training fold
        :rtype: Instances
        """
        if random is None:
            return Instances(
                javabridge.call(self.jobject, "trainCV", "(II)Lweka/core/Instances;",
                                num_folds, fold))
        else:
            return Instances(
                javabridge.call(self.jobject, "trainCV", "(IILjava/util/Random;)Lweka/core/Instances;",
                                num_folds, fold, random.jobject))

    def test_cv(self, num_folds, fold):
        """
        Generates a test fold for cross-validation.

        :param num_folds: the number of folds of cross-validation, eg 10
        :type num_folds: int
        :param fold: the current fold (0-based)
        :type fold: int
        :return: the training fold
        :rtype: Instances
        """
        return Instances(
            javabridge.call(self.jobject, "testCV", "(II)Lweka/core/Instances;",
                            num_folds, fold))

    def equal_headers(self, inst):
        """
        Compares this dataset against the given one in terms of attributes.

        :param inst: the dataset to compare against
        :type inst: Instances
        :return: None if the same, otherwise an error message
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "equalHeadersMsg", "(Lweka/core/Instances;)Ljava/lang/String;", inst.jobject)

    def copy_structure(self):
        """
        Returns a copy of the dataset structure.

        :return: the structure of the dataset
        :rtype: Instances
        """
        return Instances.copy_instances(self, 0, 0)

    @classmethod
    def copy_instances(cls, dataset, from_row=None, num_rows=None):
        """
        Creates a copy of the Instances. If either from_row or num_rows are None, then all of
        the data is being copied.

        :param dataset: the original dataset
        :type dataset: Instances
        :param from_row: the 0-based start index of the rows to copy
        :type from_row: int
        :param num_rows: the number of rows to copy
        :type num_rows: int
        :return: the copy of the data
        :rtype: Instances
        """
        if from_row is None or num_rows is None:
            return Instances(
                javabridge.make_instance(
                    "weka/core/Instances", "(Lweka/core/Instances;)V",
                    dataset.jobject))
        else:
            dataset = cls.copy_instances(dataset)
            return Instances(
                javabridge.make_instance(
                    "weka/core/Instances", "(Lweka/core/Instances;II)V",
                    dataset.jobject, from_row, num_rows))

    @classmethod
    def template_instances(cls, dataset, capacity=0):
        """
        Uses the Instances as template to create an empty dataset.

        :param dataset: the original dataset
        :type dataset: Instances
        :param capacity: how many data rows to reserve initially (see compactify)
        :type capacity: int
        :return: the empty dataset
        :rtype: Instances
        """
        return Instances(
            javabridge.make_instance(
                "weka/core/Instances", "(Lweka/core/Instances;I)V", dataset.jobject, capacity))

    @classmethod
    def create_instances(cls, name, atts, capacity):
        """
        Creates a new Instances.

        :param name: the relation name
        :type name: str
        :param atts: the list of attributes to use for the dataset
        :type atts: list of Attribute
        :param capacity: how many data rows to reserve initially (see compactify)
        :type capacity: int
        :return: the dataset
        :rtype: Instances
        """
        attributes = []
        for att in atts:
            attributes.append(att.jobject)
        return Instances(
            javabridge.make_instance(
                "weka/core/Instances", "(Ljava/lang/String;Ljava/util/ArrayList;I)V",
                name, javabridge.make_list(attributes), capacity))

    @classmethod
    def merge_instances(cls, inst1, inst2):
        """
        Merges the two datasets (side-by-side).

        :param inst1: the first dataset
        :type inst1: Instances or str
        :param inst2: the first dataset
        :type inst2: Instances
        :return: the combined dataset
        :rtype: Instances
        """
        return Instances(javabridge.static_call(
            "weka/core/Instances", "mergeInstances",
            "(Lweka/core/Instances;Lweka/core/Instances;)Lweka/core/Instances;", inst1.jobject, inst2.jobject))

    @classmethod
    def append_instances(cls, inst1, inst2):
        """
        Merges the two datasets (one-after-the-other). Throws an exception if the datasets aren't compatible.

        :param inst1: the first dataset
        :type inst1: Instances
        :param inst2: the first dataset
        :type inst2: Instances
        :return: the combined dataset
        :rtype: Instances
        """
        msg = inst1.equal_headers(inst2)
        if msg is not None:
            raise Exception("Cannot appent instances: " + msg)
        result = cls.copy_instances(inst1)
        for i in range(inst2.num_instances):
            result.add_instance(inst2.get_instance(i))
        return result

    def train_test_split(self, percentage, rnd=None):
        """
        Generates a train/test split. Creates a copy of the dataset first before applying randomization.

        :param percentage: the percentage split to use (amount to use for training; 0-100)
        :type percentage: double
        :param rnd: the random number generator to use, if None the order gets preserved
        :type rnd: Random
        :return: the train/test splits
        :rtype: tuple
        """
        if percentage <= 0:
            raise Exception("Split percentage must be > 0, provided: " + str(percentage))
        if percentage >= 100:
            raise Exception("Split percentage must be < 100, provided: " + str(percentage))
        data = self
        if rnd is not None:
            data = Instances.copy_instances(data)
            data.randomize(rnd)
        train_size = int(round(data.num_instances * percentage / 100))
        test_size = data.num_instances - train_size
        train_inst = Instances.copy_instances(data, 0, train_size)
        test_inst = Instances.copy_instances(data, train_size, test_size)
        return train_inst, test_inst

    @classmethod
    def summary(cls, inst):
        """
        Generates a summary of the dataset.

        :param inst: the dataset
        :type inst: Instances
        :return: the summary
        :rtype: str
        """
        return javabridge.call(inst.jobject, "toSummaryString", "()Ljava/lang/String;")

    def subset(self, col_range=None, col_names=None, invert_cols=False, row_range=None, invert_rows=False,
               keep_relationame=False):
        """
        Returns a subset of attributes/rows of the Instances object.
        If neither attributes nor rows have been specified a copy of the dataset
        gets returned. The invers of the specified cols/rows can be returned by setting invert_cols
        and/or invert_rows to True.
        The method uses the weka.filters.unsupervised.attribute.Remove and
        weka.filters.unsupervised.instance.RemoveRange filters under the hood.

        :param col_range: the subset of attributes to return (eg '1-3,7-12,67-last'), None for all
        :type col_range: str
        :param col_names: the list of attributes to return (list of names; case-sensitive),
                         takes precedence over col_range
        :type col_names: list
        :param invert_cols: whether to invert the returned attributes
        :type invert_cols: bool
        :param row_range: the subset of rows to return (eg '1-3,7-12,67-last'), None for all
        :type row_range: str
        :param invert_rows: whether to invert the returned rows
        :type invert_rows: bool
        :param keep_relationame: whether to keep the original relation name
        :type keep_relationame: bool
        :return: the subset
        :rtype: Instances
        """

        from weka.filters import Filter, MultiFilter

        old_relationname = self.relationname

        # turn column names into 1-based indices
        if col_names is not None:
            cols = []
            for col_name in col_names:
                att = self.attribute_by_name(col_name)
                if att is None:
                    raise Exception("Invalid attribute name: %s" % col_name)
                cols.append(str(att.index + 1))
            col_range = ",".join(cols)

        # nothing selected -> return copy
        if (col_range is None) and (row_range is None):
            return Instances.copy_instances(self)

        multi = MultiFilter()
        multi.clear()
        if col_range is not None:
            remove = Filter(classname="weka.filters.unsupervised.attribute.Remove",
                            options=["-R", col_range, ("-V" if not invert_cols else "")])
            multi.append(remove)
        if row_range is not None:
            remove = Filter(classname="weka.filters.unsupervised.instance.RemoveRange",
                            options=["-R", row_range, ("-V" if not invert_rows else "")])
            multi.append(remove)
        multi.inputformat(self)
        result = multi.filter(self)

        if keep_relationame:
            result.relationname = old_relationname

        return result


class Instance(JavaObject):
    """
    Wrapper class for weka.core.Instance.
    """
    
    def __init__(self, jobject):
        """
        Initializes the weka.core.Instance wrapper.

        :param jobject: the weka.core.Instance object to initialize with
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.core.Instance")
        super(Instance, self).__init__(jobject)

    def _make_calls(self):
        """
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        super(Instance, self)._make_calls()
        self._mc_set_value = javabridge.make_call(self.jobject, "setValue", "(ID)V")
        self._mc_get_value = javabridge.make_call(self.jobject, "value", "(I)D")
        self._mc_set_string_value = javabridge.make_call(self.jobject, "setValue", "(ILjava/lang/String;)V")
        self._mc_get_string_value = javabridge.make_call(self.jobject, "stringValue", "(I)Ljava/lang/String;")
        self._mc_set_weight = javabridge.make_call(self.jobject, "setWeight", "(D)V")
        self._mc_get_weight = javabridge.make_call(self.jobject, "weight", "()D")
        self._mc_is_missing = javabridge.make_call(self.jobject, "isMissing", "(I)Z")
        self._mc_class_index = javabridge.make_call(self.jobject, "classIndex", "()I")

    def __iter__(self):
        """
        Returns an iterator over the values.

        :return: a value iterator
        :rtype: InstanceValueIterator
        """
        return InstanceValueIterator(self)

    @property
    def dataset(self):
        """
        Returns the dataset that this instance belongs to.

        :return: the dataset or None if no dataset set
        :rtype: Instances
        """
        dataset = javabridge.call(self.jobject, "dataset", "()Lweka/core/Instances;")
        if dataset is None:
            return None
        else:
            return Instances(dataset)

    @dataset.setter
    def dataset(self, dataset):
        """
        Sets the dataset that this instance belongs to (for attribute information).

        :param dataset: the dataset this instance belongs to.
        :type dataset: Instances
        """
        javabridge.call(self.jobject, "setDataset", "(Lweka/core/Instances;)V", dataset.jobject)

    @property
    def num_attributes(self):
        """
        Returns the number of attributes.

        :return: the numer of attributes
        :rtype: int
        """
        return javabridge.call(self.jobject, "numAttributes", "()I")

    @property
    def num_classes(self):
        """
        Returns the number of class labels.

        :return: the numer of class labels
        :rtype: int
        """
        return javabridge.call(self.jobject, "numClasses", "()I")

    @property
    def class_attribute(self):
        """
        Returns the currently set class attribute.

        :return: the class attribute
        :rtype: Attribute
        """
        return Attribute(javabridge.call(self.jobject, "classAttribute", "()Lweka/core/Attribute;"))

    @property
    def class_index(self):
        """
        Returns the currently set class index.

        :return: the class index, -1 if not set
        :rtype: int
        """
        return self._mc_class_index()

    def has_class(self):
        """
        Returns whether a class attribute is set (convenience method).

        :return: whether a class attribute is currently set
        :rtype: bool
        """
        return self.class_index != -1

    def set_value(self, index, value):
        """
        Sets the internal value at the specified position (0-based).

        :param index: the 0-based index of the attribute
        :type index: int
        :param value: the internal float value to set
        :type value: float
        """
        self._mc_set_value(index, value)

    def get_value(self, index):
        """
        Returns the internal value at the specified position (0-based).

        :param index: the 0-based index of the inernal value
        :type index: int
        :return: the internal value
        :rtype: float
        """
        return self._mc_get_value(index)

    def set_string_value(self, index, s):
        """
        Sets the string value at the specified position (0-based).

        :param index: the 0-based index of the inernal value
        :type index: int
        :param s: the string value
        :type s: str
        """
        return self._mc_set_string_value(index, javabridge.get_env().new_string(s))

    def get_string_value(self, index):
        """
        Returns the string value at the specified position (0-based).

        :param index: the 0-based index of the inernal value
        :type index: int
        :return: the string value
        :rtype: str
        """
        return javabridge.get_env().get_string(self._mc_get_string_value(index))

    def get_relational_value(self, index):
        """
        Returns the relational value at the specified position (0-based).

        :param index: the 0-based index of the inernal value
        :type index: int
        :return: the relational value
        :rtype: Instances
        """
        return Instances(javabridge.call(self.jobject, "relationalValue", "(I)Lweka/core/Instances;", index))

    def set_missing(self, index):
        """
        Sets the attribute at the specified index to missing.

        :param index: the 0-based index of the attribute
        :type index: int
        """
        javabridge.call(self.jobject, "setMissing", "(I)V", index)

    def is_missing(self, index):
        """
        Returns whether the attribute at the specified index is missing.

        :param index: the 0-based index of the attribute
        :type index: int
        :return: whether the value is missing
        :rtype: bool
        """
        return self._mc_is_missing(index)

    def has_missing(self):
        """
        Returns whether at least one attribute has a missing value.

        :return: whether at least one value is missing
        :rtype: bool
        """
        return javabridge.call(self.jobject, "hasMissingValue", "()Z")

    @property
    def weight(self):
        """
        Returns the currently set weight.

        :return: the weight
        :rtype: float
        """
        return self._mc_get_weight()

    @weight.setter
    def weight(self, weight):
        """
        Sets the weight.

        :param weight: the weight to set
        :type weight: float
        """
        self._mc_set_weight(weight)

    @property
    def values(self):
        """
        Returns the internal values of this instance.

        :return: the values as numpy array
        :rtype: ndarray
        """
        return javabridge.get_env().get_double_array_elements(javabridge.call(self.jobject, "toDoubleArray", "()[D"))

    @classmethod
    def create_instance(cls, values, classname="weka.core.DenseInstance", weight=1.0):
        """
        Creates a new instance.

        :param values: the float values (internal format) to use, numpy array or list.
        :type values: ndarray or list
        :param classname: the classname of the instance (eg weka.core.DenseInstance).
        :type classname: str
        :param weight: the weight of the instance
        :type weight: float
        """
        jni_classname = classname.replace(".", "/")
        if type(values) is list:
            for i in range(len(values)):
                values[i] = float(values[i])
            values = np.array(values)
        return Instance(
            javabridge.make_instance(
                jni_classname, "(D[D)V",
                weight, javabridge.get_env().make_double_array(values)))

    @classmethod
    def create_sparse_instance(cls, values, max_values, classname="weka.core.SparseInstance", weight=1.0):
        """
        Creates a new sparse instance.

        :param values: the list of tuples (0-based index and internal format float). The indices of the
                       tuples must be in ascending order and "max_values" must be set to the maximum
                       number of attributes in the dataset.
        :type values: list
        :param max_values: the maximum number of attributes
        :type max_values: int
        :param classname: the classname of the instance (eg weka.core.SparseInstance).
        :type classname: str
        :param weight: the weight of the instance
        :type weight: float
        """
        jni_classname = classname.replace(".", "/")
        indices = []
        vals = []
        for (i, v) in values:
            indices.append(i)
            vals.append(float(v))
        indices = np.array(indices, dtype=np.int32)
        vals = np.array(vals)
        return Instance(
            javabridge.make_instance(
                jni_classname, "(D[D[II)V",
                weight, javabridge.get_env().make_double_array(vals),
                javabridge.get_env().make_int_array(indices), max_values))

    @classmethod
    def missing_value(cls):
        """
        Returns the numeric value that represents a missing value in Weka (NaN).

        :return: missing value
        :rtype: float
        """
        return missing_value()


class Attribute(JavaObject):
    """
    Wrapper class for weka.core.Attribute.
    """
    
    def __init__(self, jobject):
        """
        Initializes the weka.core.Attribute wrapper.
        :param jobject: the JB_Object
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.core.Attribute")
        super(Attribute, self).__init__(jobject)

    @property
    def name(self):
        """
        Returns the name of the attribute.

        :return: the name
        :rtype: str
        """
        return javabridge.call(self.jobject, "name", "()Ljava/lang/String;")
        
    @property
    def index(self):
        """
        Returns the index of this attribute.

        :return: the index
        :rtype: int
        """
        return javabridge.call(self.jobject, "index", "()I")

    @property
    def weight(self):
        """
        Returns the weight of the attribute.

        :return: the weight
        :rtype: float
        """
        return javabridge.call(self.jobject, "weight", "()D")

    @weight.setter
    def weight(self, weight):
        """
        Sets the weight of the attribute.

        :param weight: the weight of the attribute
        :type weight: float
        """
        javabridge.call(self.jobject, "setWeight", "(D)V", weight)

    def index_of(self, label):
        """
        Returns the index of the label in this attribute.

        :param label: the string label to get the index for
        :type label: str
        :return: the 0-based index
        :rtype: int
        """
        return javabridge.call(self.jobject, "indexOfValue", "(Ljava/lang/String;)I", label)

    def value(self, index):
        """
        Returns the label for the index.

        :param index: the 0-based index of the label to  return
        :type index: int
        :return: the label
        :rtype: str
        """
        return javabridge.call(self.jobject, "value", "(I)Ljava/lang/String;", index)

    @property
    def num_values(self):
        """
        Returns the number of labels.

        :return: the number of labels
        :rtype: int
        """
        return javabridge.call(self.jobject, "numValues", "()I")

    @property
    def values(self):
        """
        Returns the labels, strings or relation-values.

        :return: all the values, None if not NOMINAL, STRING, or RELATION
        :rtype: list
        """
        enm = javabridge.call(self.jobject, "enumerateValues", "()Ljava/util/Enumeration;")
        if enm is None:
            return None
        else:
            return typeconv.jenumeration_to_list(enm)

    @property
    def ordering(self):
        """
        Returns the ordering of the attribute.

        :return: the ordering (ORDERING_SYMBOLIC, ORDERING_ORDERED, ORDERING_MODULO)
        :rtype: int
        """
        return javabridge.call(self.jobject, "ordering", "()I")

    @property
    def type(self):
        """
        Returns the type of the attribute. See weka.core.Attribute Javadoc.

        :return: the type
        :rtype: int
        """
        return javabridge.call(self.jobject, "type", "()I")

    def type_str(self, short=False):
        """
        Returns the type of the attribute as string.

        :return: the type
        :rtype: str
        """
        if short:
            return javabridge.static_call(
                "weka/core/Attribute", "typeToStringShort", "(Lweka/core/Attribute;)Ljava/lang/String;",
                self.jobject)
        else:
            return javabridge.static_call(
                "weka/core/Attribute", "typeToString", "(Lweka/core/Attribute;)Ljava/lang/String;",
                self.jobject)

    @property
    def is_averagable(self):
        """
        Returns whether the attribute is averagable.

        :return: whether averagable
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isAveragable", "()Z")

    @property
    def is_date(self):
        """
        Returns whether the attribute is a date one.

        :return: whether date attribute
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isDate", "()Z")

    @property
    def is_nominal(self):
        """
        Returns whether the attribute is a nominal one.

        :return: whether nominal attribute
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isNominal", "()Z")

    @property
    def is_numeric(self):
        """
        Returns whether the attribute is a numeric one (date or numeric).

        :return: whether numeric attribute
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isNumeric", "()Z")

    @property
    def is_relation_valued(self):
        """
        Returns whether the attribute is a relation valued one.

        :return: whether relation valued attribute
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isRelationValued", "()Z")

    @property
    def is_string(self):
        """
        Returns whether the attribute is a string attribute.

        :return: whether string attribute
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isString", "()Z")

    @property
    def date_format(self):
        """
        Returns the format of this data attribute. See java.text.SimpleDateFormat Javadoc.

        :return: the format string
        :rtype: str
        """
        return javabridge.call(self.jobject, "getDateFormat", "()Ljava/lang/String;")

    @property
    def lower_numeric_bound(self):
        """
        Returns the lower numeric bound of the numeric attribute.

        :return: the lower bound
        :rtype: float
        """
        return javabridge.call(self.jobject, "getLowerNumericBound", "()D")

    @property
    def upper_numeric_bound(self):
        """
        Returns the upper numeric bound of the numeric attribute.

        :return: the upper bound
        :rtype: float
        """
        return javabridge.call(self.jobject, "getUpperNumericBound", "()D")

    def is_in_range(self, value):
        """
        Checks whether the value is within the bounds of the numeric attribute.

        :param value: the numeric value to check
        :type value: float
        :return: whether between lower and upper bound
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isInRange", "(D)Z", value)

    def add_string_value(self, s):
        """
        Adds the string value, returns the index.

        :param s: the string to add
        :type s: str
        :return: the index
        :rtype: int
        """
        return javabridge.call(self.jobject, "addStringValue", "(Ljava/lang/String;)I", s)

    def add_relation(self, instances):
        """
        Adds the relation value, returns the index.

        :param instances: the Instances object to add
        :type instances: Instances
        :return: the index
        :rtype: int
        """
        return javabridge.call(self.jobject, "addRelation", "(Lweka/core/Instances;)I", instances.jobject)

    def parse_date(self, s):
        """
        Parses the date string and returns the internal format value.

        :param s: the date string
        :type s: str
        :return: the internal format
        :rtype: float
        """
        return javabridge.call(self.jobject, "parseDate", "(Ljava/lang/String;)D", s)

    def equals(self, att):
        """
        Checks whether this attributes is the same as the provided one.

        :param att: the Attribute to check against
        :type att: Attribute
        :return: whether the same
        :rtype: bool
        """
        return javabridge.call(self.jobject, "equals", "(Lweka/core/Attribute;)Z", att.jobject)

    def equals_msg(self, att):
        """
        Checks whether this attributes is the same as the provided one.
        Returns None if the same, otherwise error message.

        :param att: the Attribute to check against
        :type att: Attribute
        :return: None if the same, otherwise error message
        :rtype: str
        """
        return javabridge.call(self.jobject, "equalsMsg", "(Lweka/core/Attribute;)Ljava/lang/String;", att.jobject)

    def copy(self, name=None):
        """
        Creates a copy of this attribute.

        :param name: the new name, uses the old one if None
        :type name: str
        :return: the copy of the attribute
        :rtype: Attribute
        """
        if name is None:
            return Attribute(
                javabridge.call(self.jobject, "copy", "()Ljava/lang/Object;"))
        else:
            return Attribute(
                javabridge.call(self.jobject, "copy", "(Ljava/lang/String;)Lweka/core/Attribute;", name))

    @classmethod
    def create_numeric(cls, name):
        """
        Creates a numeric attribute.

        :param name: the name of the attribute
        :type name: str
        """
        return Attribute(
            javabridge.make_instance(
                "weka/core/Attribute", "(Ljava/lang/String;)V", name))

    @classmethod
    def create_date(cls, name, formt="yyyy-MM-dd'T'HH:mm:ss"):
        """
        Creates a date attribute.

        :param name: the name of the attribute
        :type name: str
        :param formt: the date format, see Javadoc for java.text.SimpleDateFormat
        :type formt: str
        """
        return Attribute(
            javabridge.make_instance(
                "weka/core/Attribute", "(Ljava/lang/String;Ljava/lang/String;)V", name, formt))

    @classmethod
    def create_nominal(cls, name, labels):
        """
        Creates a nominal attribute.

        :param name: the name of the attribute
        :type name: str
        :param labels: the list of string labels to use
        :type labels: list
        """
        return Attribute(
            javabridge.make_instance(
                "weka/core/Attribute", "(Ljava/lang/String;Ljava/util/List;)V", name, javabridge.make_list(labels)))

    @classmethod
    def create_string(cls, name):
        """
        Creates a string attribute.

        :param name: the name of the attribute
        :type name: str
        """
        return Attribute(
            javabridge.make_instance(
                "weka/core/Attribute", "(Ljava/lang/String;Ljava/util/List;)V", name, None))

    @classmethod
    def create_relational(cls, name, inst):
        """
        Creates a relational attribute.

        :param name: the name of the attribute
        :type name: str
        :param inst: the structure of the relational attribute
        :type inst: Instances
        """
        return Attribute(
            javabridge.make_instance(
                "weka/core/Attribute", "(Ljava/lang/String;Lweka/core/Instances;)V", name, inst.jobject))


class AttributeStats(JavaObject):
    """
    Container for attribute statistics.
    """

    def __init__(self, jobject):
        """
        Initializes the container.

        :param jobject: The Java object to wrap
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.core.AttributeStats")
        super(AttributeStats, self).__init__(jobject)

    @property
    def distinct_count(self):
        """
        The number of distinct values.

        :return: The number of distinct values
        :rtype: int
        """
        return javabridge.get_field(self.jobject, "distinctCount", "I")

    @property
    def int_count(self):
        """
        The number of int-like values.

        :return: The number of int-like values
        :rtype: int
        """
        return javabridge.get_field(self.jobject, "intCount", "I")

    @property
    def missing_count(self):
        """
        The number of missing values.

        :return: The number of missing values
        :rtype: int
        """
        return javabridge.get_field(self.jobject, "missingCount", "I")

    @property
    def nominal_counts(self):
        """
        Counts of each nominal value.

        :return: Counts of each nominal value
        :rtype: ndarray
        """
        return javabridge.get_env().get_int_array_elements(
            javabridge.get_field(self.jobject, "nominalCounts", "[I"))

    @property
    def nominal_weights(self):
        """
        Weight mass for each nominal value.

        :return: Weight mass for each nominal value
        :rtype: ndarray
        """
        return javabridge.get_env().get_double_array_elements(
            javabridge.get_field(self.jobject, "nominalWeights", "[D"))

    @property
    def numeric_stats(self):
        """
        Stats on numeric value distributions.

        :return: Stats on numeric value distributions
        :rtype: NumericStats
        """
        return Stats(javabridge.get_field(self.jobject, "numericStats", "Lweka/experiment/Stats;"))

    @property
    def total_count(self):
        """
        The total number of values.

        :return: The total number of values
        :rtype: int
        """
        return javabridge.get_field(self.jobject, "totalCount", "I")

    @property
    def unique_count(self):
        """
        The number of values that only appear once.

        :return: The number of values that only appear once
        :rtype: int
        """
        return javabridge.get_field(self.jobject, "uniqueCount", "I")


class Stats(JavaObject):
    """
    Container for numeric attribute stats.
    """

    def __init__(self, jobject):
        """
        Initializes the container.

        :param jobject: The Java object to wrap
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.experiment.Stats")
        super(Stats, self).__init__(jobject)

    @property
    def count(self):
        """
        The number of values seen.

        :return: The number of values seen
        :rtype: float
        """
        return javabridge.get_field(self.jobject, "count", "D")

    @property
    def min(self):
        """
        The minimum value seen, or Double.NaN if no values seen.

        :return: The minimum value seen, or Double.NaN if no values seen
        :rtype: float
        """
        return javabridge.get_field(self.jobject, "min", "D")

    @property
    def max(self):
        """
        The maximum value seen, or Double.NaN if no values seen.

        :return: The maximum value seen, or Double.NaN if no values seen
        :rtype: float
        """
        return javabridge.get_field(self.jobject, "max", "D")

    @property
    def mean(self):
        """
        The mean of values at the last calculateDerived() call.

        :return: The mean of values at the last calculateDerived() call
        :rtype: float
        """
        return javabridge.get_field(self.jobject, "mean", "D")

    @property
    def stddev(self):
        """
        The std deviation of values at the last calculateDerived() call.

        :return: The std deviation of values at the last calculateDerived() call
        :rtype: float
        """
        return javabridge.get_field(self.jobject, "stdDev", "D")

    @property
    def sum(self):
        """
        The sum of values seen.

        :return: The sum of values seen
        :rtype: float
        """
        return javabridge.get_field(self.jobject, "sum", "D")

    @property
    def sumsq(self):
        """
        The sum of values squared seen.

        :return: The sum of values squared seen
        :rtype: float
        """
        return javabridge.get_field(self.jobject, "sumSq", "D")


class InstanceIterator(object):
    """
    Iterator for rows in an Instances object.
    """
    def __init__(self, data):
        """
        Initializes the iterator.

        :param data: the Instances object to iterate over
        :type data: Instances
        """
        self.data = data
        self.row = 0

    def __iter__(self):
        """
        Returns itself.
        """
        return self

    def __next__(self):
        """
        Returns the next row from the Instances object.

        :return: the next Instance object
        :rtype: Instance
        """
        if self.row < self.data.num_instances:
            index = self.row
            self.row += 1
            return self.data.get_instance(index)
        else:
            raise StopIteration()


class AttributeIterator(object):
    """
    Iterator for attributes in an Instances object.
    """
    def __init__(self, data):
        """
        Initializes the iterator.

        :param data: the Instances object to iterate over
        :type data: Instances
        """
        self.data = data
        self.col = 0

    def __iter__(self):
        """
        Returns itself.
        """
        return self

    def __next__(self):
        """
        Returns the next attribute from the Instances object.

        :return: the next Attribute object
        :rtype: Attribute
        """
        if self.col < self.data.num_attributes:
            index = self.col
            self.col += 1
            return self.data.attribute(index)
        else:
            raise StopIteration()


class InstanceValueIterator(object):
    """
    Iterator for values in an Instance object.
    """
    def __init__(self, data):
        """
        Initializes the iterator.

        :param data: the Instance object to iterate over
        :type data: Instance
        """
        self.data = data
        self.col = 0

    def __iter__(self):
        """
        Returns itself.
        """
        return self

    def __next__(self):
        """
        Returns the next value from the Instance object.
        
        :return: the next value, depending on the attribute that can be either a number of a string
        :rtype: str or float
        """
        if self.col < self.data.num_attributes:
            index = self.col
            self.col += 1
            if self.data.dataset.attribute(index).is_numeric:
                return self.data.get_value(index)
            else:
                return self.data.get_string_value(index)
        else:
            raise StopIteration()


def create_instances_from_lists(x, y=None, name="data"):
    """
    Allows the generation of an Instances object from a list of lists for X and a list for Y (optional).
    Data can be numeric, string or bytes. Attributes can be converted to nominal with the
    weka.filters.unsupervised.attribute.NumericToNominal filter.

    :param x: the input variables (row wise)
    :type x: list of list
    :param y: the output variable (optional)
    :type y: list
    :param name: the name of the dataset
    :type name: str
    :return: the generated dataset
    :rtype: Instances
    """
    if y is not None:
        if len(x) != len(y):
            raise Exception("Dimensions of x and y differ: " + str(len(x)) + " != " + str(len(y)))

    # create header
    atts = []
    type_x = []
    for i in range(len(x[0])):
        if isinstance(x[0][i], float) or isinstance(x[0][i], int):
            type_x.append("N")
            atts.append(Attribute.create_numeric("x" + str(i+1)))
        elif isinstance(x[0][i], bytes):
            type_x.append("B")
            atts.append(Attribute.create_string("x" + str(i+1)))
        elif isinstance(x[0][i], str):
            type_x.append("S")
            atts.append(Attribute.create_string("x" + str(i+1)))
        else:
            raise Exception("Only float, int, bytes and str are supported, #" + str(i) + ": " + str(type(x[i][0])))

    type_y = ""
    if y is not None:
        if isinstance(y[0], float) or isinstance(y[0], int):
            type_y = "N"
            atts.append(Attribute.create_numeric("y"))
        elif isinstance(y[0], bytes):
            type_y = "B"
            atts.append(Attribute.create_string("y"))
        elif isinstance(y[0], str):
            type_y = "S"
            atts.append(Attribute.create_string("y"))
        else:
            raise Exception("Only float, int, bytes and str are supported for y: " + str(type(y[0])))

    result = Instances.create_instances(name, atts, len(x))

    # add data
    for i in range(len(x)):
        values = []
        for n in range(len(x[i])):
            if type_x[n] == "N":
                values.append(x[i][n])
            elif type_x[n] == "B":
                values.append(result.attribute(n).add_string_value(x[i][n].decode("utf-8")))
            else:
                values.append(result.attribute(n).add_string_value(x[i][n]))
        if y is not None:
            if type_y == "N":
                values.append(y[i])
            elif type_y == "B":
                values.append(result.attribute(result.num_attributes - 1).add_string_value(y[i].decode("utf-8")))
            else:
                values.append(result.attribute(result.num_attributes - 1).add_string_value(y[i]))
        result.add_instance(Instance.create_instance(values))

    return result


def create_instances_from_matrices(x, y=None, name="data"):
    """
    Allows the generation of an Instances object from a 2-dimensional matrix for X and a
    1-dimensional matrix for Y (optional).
    Data can be numeric, string or bytes. Attributes can be converted to nominal with the
    weka.filters.unsupervised.attribute.NumericToNominal filter.

    :param x: the input variables
    :type x: ndarray
    :param y: the output variable (optional)
    :type y: ndarray
    :param name: the name of the dataset
    :type name: str
    :return: the generated dataset
    :rtype: Instances
    """
    if y is not None:
        if len(x) != len(y):
            raise Exception("Dimensions of x and y differ: " + str(len(x)) + " != " + str(len(y)))

    # create header
    atts = []
    type_x = []
    for i in range(len(x[0])):
        try:
            len(x.dtype)
            if np.issubdtype(x.dtype[i], np.number):
                type_x.append("N")  # number
                atts.append(Attribute.create_numeric("x" + str(i+1)))
            elif np.issubdtype(x.dtype[i], np.str_):
                type_x.append("S")  # string
                atts.append(Attribute.create_string("x" + str(i+1)))
            else:
                type_x.append("B")  # bytes
                atts.append(Attribute.create_string("x" + str(i+1)))
        except:
            type_x.append("N")  # number
            atts.append(Attribute.create_numeric("x" + str(i+1)))
    type_y = ""
    if y is not None:
        if np.issubdtype(y.dtype, np.number):
            type_y = "N"  # number
            atts.append(Attribute.create_numeric("y"))
        elif np.issubdtype(y.dtype, np.str_):
            type_y = "S"  # string
            atts.append(Attribute.create_string("y"))
        else:
            type_y = "B"  # bytes
            atts.append(Attribute.create_string("y"))

    result = Instances.create_instances(name, atts, len(x))

    # add data
    for i in range(len(x)):
        values = []
        for n in range(len(x[i])):
            if type_x[n] == "N":
                values.append(x[i][n])
            elif type_x[n] == "S":
                values.append(result.attribute(n).add_string_value(x[i][n]))
            else:
                values.append(result.attribute(n).add_string_value(x[i][n].decode("utf-8")))
        if y is not None:
            if type_y == "N":
                values.append(y[i])
            elif type_y == "S":
                values.append(result.attribute(result.num_attributes - 1).add_string_value(y[i]))
            else:
                values.append(result.attribute(result.num_attributes - 1).add_string_value(y[i].decode("utf-8")))
        result.add_instance(Instance.create_instance(values))

    return result


def missing_value():
    """
    Returns the value that represents missing values in Weka (NaN).

    :return: missing value
    :rtype: float
    """
    return float("NaN")
