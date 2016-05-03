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
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import os
import sys
import argparse
import weka.core.jvm as jvm
from weka.core.classes import OptionHandler, join_options
from weka.core.capabilities import Capabilities
from weka.core.converters import Loader
from weka.core.converters import Saver
from weka.core.dataset import Instances
from weka.core.dataset import Instance
from weka.core.stemmers import Stemmer
from weka.core.stopwords import Stopwords
from weka.core.tokenizers import Tokenizer

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
        self.__input = javabridge.make_call(self.jobject, "input", "(Lweka/core/Instance;)Z")
        self.__batchfinished = javabridge.make_call(self.jobject, "batchFinished", "()Z")
        self.__output = javabridge.make_call(self.jobject, "output", "()Lweka/core/Instance;")
        self.__outputformat = javabridge.make_call(self.jobject, "getOutputFormat", "()Lweka/core/Instances;")

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
        return self.__input(inst.jobject)

    def batch_finished(self):
        """
        Signals the filter that the batch of data has finished.

        :return: True if instances can be collected from the output
        :rtype: bool
        """
        return self.__batchfinished()

    def outputformat(self):
        """
        Returns the output format.

        :return: the output format
        :rtype: Instances
        """
        inst = self.__outputformat()
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
        return Instance(jobject=self.__output())

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


def main():
    """
    Runs a filter from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.
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
    parsed = parser.parse_args()
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
    except Exception as e:
        print(e)
    finally:
        jvm.stop()

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
