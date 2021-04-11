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

# associations.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import os
import sys
import argparse
import traceback
import weka.core.jvm as jvm
import weka.core.converters as converters
from weka.core.classes import OptionHandler, JavaObject, join_options
from weka.core.capabilities import Capabilities
from weka.core.dataset import Attribute
from weka.core.typeconv import jstring_array_to_list

# logging setup
logger = logging.getLogger("weka.associations")


class Item(JavaObject):
    """
    Wrapper for weka.associations.Item class.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the Item object to wrap
        :type jobject: JB_Object
        """

        if jobject is None:
            raise Exception("No Item JB_Object provided!")
        self.enforce_type(jobject, "weka.associations.Item")
        super(Item, self).__init__(jobject)

    def __compareto__(self, other):
        """
        Return the comparison result with the other rule.

        :param other: the other rule to compare with
        :type other: Item
        :return: the integer result, <0 is less than, =0 is equal to, >0 is greater than
        :rtype: int
        """
        return javabridge.call(self.jobject, "compareTo", "(Lweka/associations/Item;)I", other.jobject)

    def __lt__(self, other):
        """
        Checks self < other.

        :param other: the item to compare with
        :type other: Item
        :return: whether less than the other item
        :rtype: bool
        """
        return self.__compareto__(other) < 0

    def __le__(self, other):
        """
        Checks self <= other.

        :param other: the item to compare with
        :type other: Item
        :return: whether less or equal than the other item
        :rtype: bool
        """
        return self.__compareto__(other) <= 0

    def decrease_frequency(self, frequency=None):
        """
        Decreases the frequency.

        :param frequency: the frequency to decrease by, 1 if None
        :type frequency: int
        """
        if frequency is None:
            javabridge.call(self.jobject, "decreaseFrequency", "()V")
        else:
            javabridge.call(self.jobject, "decreaseFrequency", "(I)V", frequency)

    def increase_frequency(self, frequency=None):
        """
        Increases the frequency.

        :param frequency: the frequency to increase by, 1 if None
        :type frequency: int
        """
        if frequency is None:
            javabridge.call(self.jobject, "increaseFrequency", "()V")
        else:
            javabridge.call(self.jobject, "increaseFrequency", "(I)V", frequency)

    def __eq__(self, other):
        """
        Returns whether this object is the same as the other one.

        :param other: the object to compare with
        :type other: Item
        :return: True if the same
        :rtype: bool
        """
        return javabridge.call(self.jobject, "equals", "(Ljava/lang/Object;)Z", other.jobject)

    def __ge__(self, other):
        """
        Checks self >= other.

        :param other: the item to compare with
        :type other: Item
        :return: whether greater or equal than the other item
        :rtype: bool
        """
        return self.__compareto__(other) >= 0

    def __gt__(self, other):
        """
        Checks self > other.

        :param other: the item to compare with
        :type other: Item
        :return: whether greater than the other item
        :rtype: bool
        """
        return self.__compareto__(other) > 0

    def __str__(self):
        """
        Returns the item as string.

        :return: the item as string
        :rtype: str
        """
        return javabridge.call(self.jobject, "toString", "()Ljava/lang/String;")

    @property
    def frequency(self):
        """
        Returns the frequency.

        :return: the frequency
        :rtype: int
        """
        return javabridge.call(self.jobject, "getFrequency", "()I")

    @property
    def attribute(self):
        """
        Returns the attribute.

        :return: the attribute
        :rtype: Attribute
        """
        return Attribute(javabridge.call(self.jobject, "getAttribute", "()Lweka/core/Attribute;"))

    @property
    def comparison(self):
        """
        Returns the comparison operator as string.

        :return: the comparison iterator
        :rtype: str
        """
        return Attribute(javabridge.call(self.jobject, "getComparisonAsString", "()Ljava/lang/String;"))

    @property
    def item_value(self):
        """
        Returns the item value as string.

        :return: the item value
        :rtype: str
        """
        return Attribute(javabridge.call(self.jobject, "getItemValueAsString", "()Ljava/lang/String;"))


class AssociationRule(JavaObject):
    """
    Wrapper for weka.associations.AssociationRule class.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the AssociationRule object to wrap
        :type jobject: JB_Object
        """
        if jobject is None:
            raise Exception("No AssociationRule JB_Object provided!")
        self.enforce_type(jobject, "weka.associations.AssociationRule")
        super(AssociationRule, self).__init__(jobject)

    def __compareto__(self, other):
        """
        Return the comparison result with the other rule.

        :param other: the other rule to compare with
        :type other: AssociationRule
        :return: the integer result, <0 is less than, =0 is equal to, >0 is greater than
        :rtype: int
        """
        return javabridge.call(self.jobject, "compareTo", "(Lweka/associations/AssociationRule;)I", other.jobject)

    def __lt__(self, other):
        """
        Checks self < other.

        :param other: the rule to compare with
        :type other: AssociationRule
        :return: whether less than the other rule
        :rtype: bool
        """
        return self.__compareto__(other) < 0

    def __le__(self, other):
        """
        Checks self <= other.

        :param other: the rule to compare with
        :type other: AssociationRule
        :return: whether less or equal than the other rule
        :rtype: bool
        """
        return self.__compareto__(other) <= 0

    def __eq__(self, other):
        """
        Returns whether this object is the same as the other one.

        :param other: the object to compare with
        :type other: AssociationRule
        :return: True if the same
        :rtype: bool
        """
        return javabridge.call(self.jobject, "equals", "(Ljava/lang/Object;)Z", other.jobject)

    def __ge__(self, other):
        """
        Checks self >= other.

        :param other: the rule to compare with
        :type other: AssociationRule
        :return: whether greater or equal than the other rule
        :rtype: bool
        """
        return self.__compareto__(other) >= 0

    def __gt__(self, other):
        """
        Checks self > other.

        :param other: the rule to compare with
        :type other: AssociationRule
        :return: whether greater than the other rule
        :rtype: bool
        """
        return self.__compareto__(other) > 0

    @property
    def consequence(self):
        """
        Get the the consequence.

        :return: the consequence, list of Item objects
        :rtype: list
        """
        items = javabridge.get_collection_wrapper(
            javabridge.call(self.jobject, "getConsequence", "()Ljava/util/Collection;"))
        result = []
        for item in items:
            result.append(Item(item))
        return result

    @property
    def consequence_support(self):
        """
        Get the support for the consequence.

        :return: the support
        :rtype: int
        """
        return javabridge.call(self.jobject, "getConsequenceSupport", "()I")

    @property
    def premise(self):
        """
        Get the the premise.

        :return: the premise, list of Item objects
        :rtype: list
        """
        items = javabridge.get_collection_wrapper(
            javabridge.call(self.jobject, "getPremise", "()Ljava/util/Collection;"))
        result = []
        for item in items:
            result.append(Item(item))
        return result

    @property
    def premise_support(self):
        """
        Get the support for the premise.

        :return: the support
        :rtype: int
        """
        return javabridge.call(self.jobject, "getPremiseSupport", "()I")

    @property
    def total_support(self):
        """
        Get the total support.

        :return: the support
        :rtype: int
        """
        return javabridge.call(self.jobject, "getTotalSupport", "()I")

    @property
    def total_transactions(self):
        """
        Get the total transactions.

        :return: the transactions
        :rtype: int
        """
        return javabridge.call(self.jobject, "getTotalTransactions", "()I")

    @property
    def metric_names(self):
        """
        Returns the metric names for the rule.

        :return: the metric names
        :rtype: list
        """
        return jstring_array_to_list(javabridge.call(self.jobject, "getMetricNamesForRule", "()[Ljava/lang/String;"))

    @property
    def metric_values(self):
        """
        Returns the metric values for the rule.

        :return: the metric values
        :rtype: ndarray
        """
        return javabridge.get_env().get_double_array_elements(
            javabridge.call(self.jobject, "getMetricValuesForRule", "()[D"))

    def metric_value(self, name):
        """
        Returns the named metric value for the rule.

        :param name: the name of the metric
        :type name: str
        :return: the metric value
        :rtype: float
        """
        return javabridge.call(self.jobject, "getNamedMetricValue", "(Ljava/lang/String;)D", name)

    @property
    def primary_metric_name(self):
        """
        Returns the primary metric name for the rule.

        :return: the metric name
        :rtype: str
        """
        return javabridge.call(self.jobject, "getPrimaryMetricName", "()Ljava/lang/String;")

    @property
    def primary_metric_value(self):
        """
        Returns the primary metric value for the rule.

        :return: the metric value
        :rtype: float
        """
        return javabridge.call(self.jobject, "getPrimaryMetricValue", "()D")
    
    def to_dict(self):
        """
        Builds a dictionary with the properties of the AssociationRule object.

        :return: the AssociationRule dictionary
        :rtype: dict
        """
        rule = {
            'premise': self.premise,
            'premise_support': self.premise_support,
            'consequence': self.consequence,
            'consequence_support': self.consequence_support,
            'total_support': self.total_support
        }
        index_names = [x.lower() for x in self.metric_names]
        metrics = dict(zip(index_names, self.metric_values))
        rule.update(metrics)
        return rule


class AssociationRulesIterator(object):
    """
    Iterator for weka.associations.AssociationRules class.
    """

    def __init__(self, rules):
        """
        Initializes with the rules.

        :param rules: the rules to use
        :type rules: AssociationRules
        """
        self.rules = rules
        self.index = 0
        self.length = len(rules)

    def __iter__(self):
        """
        Returns itself.
        """
        return self

    def __next__(self):
        """
        Returns the next rule.

        :return: the next rule object
        :rtype: AssociationRule
        """
        if self.index < self.length:
            index = self.index
            self.index += 1
            return self.rules[index]
        else:
            raise StopIteration()


class AssociationRules(JavaObject):
    """
    Wrapper for weka.associations.AssociationRules class.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper.

        :param jobject: the AssociationRules object to wrap
        :type jobject: JB_Object
        """
        if jobject is None:
            raise Exception("No AssociationRules JB_Object provided!")
        self.enforce_type(jobject, "weka.associations.AssociationRules")
        super(AssociationRules, self).__init__(jobject)

    def __len__(self):
        """
        Returns the number of rules available.

        :return: the number of rules
        :rtype: int
        """
        return javabridge.call(self.jobject, "getNumRules", "()I")

    def __getitem__(self, item):
        """
        Returns the specified item, using 0-based indices.

        :param item: the 0-based index
        :type item: int
        :return: the AssociationRule
        :rtype: AssociationRule
        """
        rules = javabridge.get_collection_wrapper(
            javabridge.call(self.jobject, "getRules", "()Ljava/util/List;"))
        return AssociationRule(rules[item])

    def __str__(self):
        """
        Returns a short description of the rules.

        :return: short description
        :rtype: str
        """
        return str(len(self)) + " rules generated by " + self.producer

    def __iter__(self):
        """
        Returns an iterator for the rules.

        :return: the iterator
        :rtype: AssociationRulesIterator
        """
        return AssociationRulesIterator(self)

    @property
    def producer(self):
        """
        Returns a string describing the producer that generated these rules.

        :return: the producer
        :rtype: str
        """
        return javabridge.call(self.jobject, "getProducer", "()Ljava/lang/String;")

    @producer.setter
    def producer(self, producer):
        """"
        Sets the string describing the producer that generated these rules.

        :param producer: the producer
        :type producer: str
        """
        javabridge.call(self.jobject, "setProducer", "(Ljava/lang/String;)V", producer)
    
    def to_dict(self):
        """
        Returns a list of association rules in dict format

        :return: the association rules
        :rtype: list
        """
        rules = []
        for rule in self:
            rules.append(rule.to_dict())
        return rules


class Associator(OptionHandler):
    """
    Wrapper class for associators.
    """

    def __init__(self, classname=None, jobject=None, options=None):
        """
        Initializes the specified associator using either the classname or the supplied JB_Object.

        :param classname: the classname of the associator
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Associator.new_instance(classname)
        self.enforce_type(jobject, "weka.associations.Associator")
        self._header = None
        super(Associator, self).__init__(jobject=jobject, options=options)

    @property
    def capabilities(self):
        """
        Returns the capabilities of the associator.

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

    def build_associations(self, data):
        """
        Builds the associator with the data.

        :param data: the data to train the associator with
        :type data: Instances
        """
        self._header = data.copy_structure()
        javabridge.call(self.jobject, "buildAssociations", "(Lweka/core/Instances;)V", data.jobject)

    def can_produce_rules(self):
        """
        Checks whether association rules can be generated.

        :return: whether scheme implements AssociationRulesProducer interface and association rules can be generated
        :rtype: bool
        """
        if not self.check_type(self.jobject, "weka.associations.AssociationRulesProducer"):
            return False
        return javabridge.call(self.jobject, "canProduceRules", "()Z")

    def association_rules(self):
        """
        Returns association rules that were generated. Only if implements AssociationRulesProducer.

        :return: the association rules that were generated
        :rtype: AssociationRules
        """
        if not self.check_type(self.jobject, "weka.associations.AssociationRulesProducer"):
            return None
        return AssociationRules(
            javabridge.call(self.jobject, "getAssociationRules", "()Lweka/associations/AssociationRules;"))

    @property
    def rule_metric_names(self):
        """
        Returns the rule metric names of the association rules. Only if implements AssociationRulesProducer.

        :return: the metric names
        :rtype: list
        """
        if not self.check_type(self.jobject, "weka.associations.AssociationRulesProducer"):
            return None
        return jstring_array_to_list(
            javabridge.call(self.jobject, "getRuleMetricNames", "()[Ljava/lang/String;"))

    @classmethod
    def make_copy(cls, associator):
        """
        Creates a copy of the clusterer.

        :param associator: the associator to copy
        :type associator: Associator
        :return: the copy of the associator
        :rtype: Associator
        """
        return Associator(
            jobject=javabridge.static_call(
                "weka/associations/AbstractAssociator", "makeCopy",
                "(Lweka/associations/Associator;)Lweka/associations/Associator;", associator.jobject))


def main(args=None):
    """
    Runs a associator from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Executes an associator from the command-line. Calls JVM start/stop automatically.')
    parser.add_argument("-j", metavar="classpath", dest="classpath", help="additional classpath, jars/directories")
    parser.add_argument("-X", metavar="heap", dest="heap", help="max heap size for jvm, e.g., 512m")
    parser.add_argument("-t", metavar="train", dest="train", required=True, help="training set file")
    parser.add_argument("associator", help="associator classname, e.g., weka.associations.Apriori")
    parser.add_argument("option", nargs=argparse.REMAINDER, help="additional associator options")
    parsed = parser.parse_args(args=args)
    jars = []
    if parsed.classpath is not None:
        jars = parsed.classpath.split(os.pathsep)

    jvm.start(jars, max_heap_size=parsed.heap, packages=True)

    logger.debug("Commandline: " + join_options(sys.argv[1:]))

    try:
        associator = Associator(classname=parsed.associator)
        if len(parsed.option) > 0:
            associator.options = parsed.option
        loader = converters.loader_for_file(parsed.train)
        data = loader.load_file(parsed.train)
        associator.build_associations(data)
        print(str(associator))
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
