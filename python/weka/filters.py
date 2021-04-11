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

# filters.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import os
import sys
import argparse
import traceback
import weka.core.jvm as jvm
from weka.core.classes import serialization_write, serialization_read_all
from weka.core.classes import OptionHandler, join_options
from weka.core.capabilities import Capabilities
from weka.core.converters import Loader
from weka.core.converters import Saver
from weka.core.dataset import Instances
from weka.core.dataset import Instance
from weka.core.stemmers import Stemmer
from weka.core.stopwords import Stopwords
from weka.core.tokenizers import Tokenizer
from weka.attribute_selection import ASEvaluation, ASSearch

# logging setup
logger = logging.getLogger("weka.filters")


class Filter(OptionHandler):
    """
    Wrapper class for filters.
    """

    def __init__(self, classname="weka.filters.AllFilter", jobject=None, options=None):
        """
        Initializes the specified filter using either the classname or the supplied JB_Object.

        :param classname: the classname of the filter
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Filter.new_instance(classname)
        self.enforce_type(jobject, "weka.filters.Filter")
        super(Filter, self).__init__(jobject=jobject, options=options)

    def _make_calls(self):
        """
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        super(Filter, self)._make_calls()
        self._mc_input = javabridge.make_call(self.jobject, "input", "(Lweka/core/Instance;)Z")
        self._mc_batchfinished = javabridge.make_call(self.jobject, "batchFinished", "()Z")
        self._mc_output = javabridge.make_call(self.jobject, "output", "()Lweka/core/Instance;")
        self._mc_outputformat = javabridge.make_call(self.jobject, "getOutputFormat", "()Lweka/core/Instances;")

    def capabilities(self):
        """
        Returns the capabilities of the filter.

        :return: the capabilities
        :rtype: Capabilities
        """
        return Capabilities(javabridge.call(self.jobject, "getCapabilities", "()Lweka/core/Capabilities;"))

    def inputformat(self, data):
        """
        Sets the input format.

        :param data: the data to use as input
        :type data: Instances
        """
        return javabridge.call(self.jobject, "setInputFormat", "(Lweka/core/Instances;)Z", data.jobject)

    def input(self, inst):
        """
        Inputs the Instance.

        :param inst: the instance to filter
        :type inst: Instance
        :return: True if filtered can be collected from output
        :rtype: bool
        """
        return self._mc_input(inst.jobject)

    def batch_finished(self):
        """
        Signals the filter that the batch of data has finished.

        :return: True if instances can be collected from the output
        :rtype: bool
        """
        return self._mc_batchfinished()

    def outputformat(self):
        """
        Returns the output format.

        :return: the output format
        :rtype: Instances
        """
        inst = self._mc_outputformat()
        if inst is None:
            return None
        else:
            return Instances(inst)

    def output(self):
        """
        Outputs the filtered Instance.

        :return: the filtered instance
        :rtype: an Instance object
        """
        return Instance(jobject=self._mc_output())

    def filter(self, data):
        """
        Filters the dataset(s). When providing a list, this can be used to create compatible train/test sets,
        since the filter only gets initialized with the first dataset and all subsequent datasets get transformed
        using the same setup.

        NB: inputformat(Instances) must have been called beforehand.

        :param data: the Instances to filter
        :type data: Instances or list of Instances
        :return: the filtered Instances object(s)
        :rtype: Instances or list of Instances
        """
        if isinstance(data, list):
            result = []
            for d in data:
                result.append(Instances(javabridge.static_call(
                    "Lweka/filters/Filter;", "useFilter",
                    "(Lweka/core/Instances;Lweka/filters/Filter;)Lweka/core/Instances;",
                    d.jobject, self.jobject)))
            return result
        else:
            return Instances(javabridge.static_call(
                "Lweka/filters/Filter;", "useFilter",
                "(Lweka/core/Instances;Lweka/filters/Filter;)Lweka/core/Instances;",
                data.jobject, self.jobject))

    def to_source(self, classname, data):
        """
        Returns the model as Java source code if the classifier implements weka.filters.Sourcable.

        :param classname: the classname for the generated Java code
        :type classname: str
        :param data: the dataset used for initializing the filter
        :type data: Instances
        :return: the model as source code string
        :rtype: str
        """
        if not self.check_type(self.jobject, "weka.filters.Sourcable"):
            return None
        return javabridge.call(self.jobject, "toSource", "(Ljava/lang/String;Lweka/core/Instances;)Ljava/lang/String;", classname, data.jobject)

    @classmethod
    def make_copy(cls, flter):
        """
        Creates a copy of the filter.

        :param flter: the filter to copy
        :type flter: Filter
        :return: the copy of the filter
        :rtype: Filter
        """
        return Filter(
            jobject=javabridge.static_call(
                "weka/filters/Filter", "makeCopy",
                "(Lweka/filters/Filter;)Lweka/filters/Filter;", flter.jobject))

    @classmethod
    def deserialize(cls, ser_file):
        """
        Deserializes a filter from a file.

        :param ser_file: the file to deserialize from
        :type ser_file: str
        :return: model
        :rtype: Filter
        """

        objs = serialization_read_all(ser_file)
        if len(objs) == 1:
            return Filter(jobject=objs[0])
        else:
            raise Exception(
                "Excepted one object in the model file (%s), but encountered: %d" % (ser_file, len(objs)))

    def serialize(self, ser_file):
        """
        Serializes the filter to the specified file.

        :param ser_file: the file to save the filter to
        :type ser_file: str
        """

        serialization_write(ser_file, self)


class MultiFilter(Filter):
    """
    Wrapper class for weka.filters.MultiFilter.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the MultiFilter instance using either creating new instance or using the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: list of commandline options
        :type options: list
        """
        if jobject is None:
            classname = "weka.filters.MultiFilter"
            jobject = MultiFilter.new_instance(classname)
        self.enforce_type(jobject, "weka.filters.MultiFilter")
        super(MultiFilter, self).__init__(jobject=jobject, options=options)

    @property
    def filters(self):
        """
        Returns the list of base filters.

        :return: the filter list
        :rtype: list
        """
        objects = javabridge.get_env().get_object_array_elements(
            javabridge.call(self.jobject, "getFilters", "()[Lweka/filters/Filter;"))
        result = []
        for obj in objects:
            result.append(Filter(jobject=obj))
        return result

    @filters.setter
    def filters(self, filters):
        """
        Sets the base filters.

        :param filters: the list of base filters to use
        :type filters: list
        """
        obj = []
        for fltr in filters:
            obj.append(fltr.jobject)
        javabridge.call(self.jobject, "setFilters", "([Lweka/filters/Filter;)V", obj)

    def clear(self):
        """
        Removes all filters.
        """
        self.filters = []

    def append(self, filter):
        """
        Appends the filter to the current list of filters.

        :param filter: the filter to add
        :type filter: Filter
        """
        l = self.filters
        l.append(filter)
        self.filters = l


class StringToWordVector(Filter):
    """
    Wrapper class for weka.filters.unsupervised.attribute.StringToWordVector.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the StringToWordVector instance using either creating new instance or using the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: list of commandline options
        :type options: list
        """
        if jobject is None:
            classname = "weka.filters.unsupervised.attribute.StringToWordVector"
            jobject = StringToWordVector.new_instance(classname)
        self.enforce_type(jobject, "weka.filters.unsupervised.attribute.StringToWordVector")
        super(StringToWordVector, self).__init__(jobject=jobject, options=options)

    @property
    def stemmer(self):
        """
        Returns the stemmer.

        :return: the stemmer
        :rtype: Stemmer
        """
        return Stemmer(
            jobject=javabridge.call(self.jobject, "getStemmer", "()Lweka/core/stemmers/Stemmer;"))

    @stemmer.setter
    def stemmer(self, stemmer):
        """
        Sets the stemmer.

        :param stemmer: the stemmer to use
        :type stemmer: Stemmer
        """
        javabridge.call(
            self.jobject, "setStemmer", "(Lweka/core/stemmers/Stemmer;)V", stemmer.jobject)

    @property
    def stopwords(self):
        """
        Returns the stopwords handler.

        :return: the stopwords handler
        :rtype: Stopwords
        """
        return Stopwords(
            jobject=javabridge.call(self.jobject, "getStopwordsHandler", "()Lweka/core/stopwords/StopwordsHandler;"))

    @stopwords.setter
    def stopwords(self, stopwords):
        """
        Sets the stopwords handler.

        :param stopwords: the stopwords handler to use
        :type stopwords: Stopwords
        """
        javabridge.call(
            self.jobject, "setStopwordsHandler", "(Lweka/core/stopwords/StopwordsHandler;)V", stopwords.jobject)

    @property
    def tokenizer(self):
        """
        Returns the tokenizer.

        :return: the tokenizer
        :rtype: Tokenizer
        """
        return Tokenizer(
            jobject=javabridge.call(self.jobject, "getTokenizer", "()Lweka/core/tokenizers/Tokenizer;"))

    @tokenizer.setter
    def tokenizer(self, tokenizer):
        """
        Sets the tokenizer.

        :param tokenizer: the tokenizer to use
        :type tokenizer: Tokenizer
        """
        javabridge.call(
            self.jobject, "setTokenizer", "(Lweka/core/tokenizers/Tokenizer;)V", tokenizer.jobject)


class AttributeSelection(Filter):
    """
    Wrapper class for weka.filters.supervised.attribute.AttributeSelection.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the AttributeSelection instance using either creating new instance or using the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: list of commandline options
        :type options: list
        """
        if jobject is None:
            classname = "weka.filters.supervised.attribute.AttributeSelection"
            jobject = AttributeSelection.new_instance(classname)
        self.enforce_type(jobject, "weka.filters.supervised.attribute.AttributeSelection")
        super(AttributeSelection, self).__init__(jobject=jobject, options=options)

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


def main(args=None):
    """
    Runs a filter from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Executes a filter from the command-line. Calls JVM start/stop automatically.')
    parser.add_argument("-j", metavar="classpath", dest="classpath", help="additional classpath, jars/directories")
    parser.add_argument("-X", metavar="heap", dest="heap", help="max heap size for jvm, e.g., 512m")
    parser.add_argument("-i", metavar="input1", dest="input1", required=True, help="input file 1")
    parser.add_argument("-o", metavar="output1", dest="output1", required=True, help="output file 1")
    parser.add_argument("-r", metavar="input2", dest="input2", help="input file 2")
    parser.add_argument("-s", metavar="output2", dest="output2", help="output file 2")
    parser.add_argument("-c", metavar="classindex", default="-1", dest="classindex",
                        help="1-based class attribute index")
    parser.add_argument("filter", help="filter classname, e.g., weka.filters.AllFilter")
    parser.add_argument("option", nargs=argparse.REMAINDER, help="additional filter options")
    parsed = parser.parse_args(args=args)
    if parsed.input2 is None and parsed.output2 is not None:
        raise Exception("No second input file provided ('-r ...')!")

    jars = []
    if parsed.classpath is not None:
        jars = parsed.classpath.split(os.pathsep)
    params = []
    if parsed.input1 is not None:
        params.extend(["-i", parsed.input1])
    if parsed.output1 is not None:
        params.extend(["-o", parsed.output1])
    if parsed.input2 is not None:
        params.extend(["-r", parsed.input2])
    if parsed.output2 is not None:
        params.extend(["-s", parsed.output2])
    if parsed.classindex is not None:
        params.extend(["-c", parsed.classindex])

    jvm.start(jars, max_heap_size=parsed.heap, packages=True)

    logger.debug("Commandline: " + join_options(sys.argv[1:]))

    try:
        flter = Filter(parsed.filter)
        if len(parsed.option) > 0:
            flter.options = parsed.option
        loader = Loader(classname="weka.core.converters.ArffLoader")
        in1 = loader.load_file(parsed.input1)
        cls = parsed.classindex
        if str(parsed.classindex) == "first":
            cls = "0"
        if str(parsed.classindex) == "last":
            cls = str(in1.num_attributes - 1)
        in1.class_index = int(cls)
        flter.inputformat(in1)
        out1 = flter.filter(in1)
        saver = Saver(classname="weka.core.converters.ArffSaver")
        saver.save_file(out1, parsed.output1)
        if parsed.input2 is not None:
            in2 = loader.load_file(parsed.input2)
            in2.class_index = int(cls)
            out2 = flter.filter(in2)
            saver.save_file(out2, parsed.output2)
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
