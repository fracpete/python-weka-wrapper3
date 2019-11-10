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

# datagenerators.py
# Copyright (C) 2014-2019 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import os
import sys
import argparse
import traceback
import weka.core.jvm as jvm
import weka.core.classes as classes
from weka.core.classes import OptionHandler, join_options, to_commandline, from_commandline
from weka.core.dataset import Instances, Instance

# logging setup
logger = logging.getLogger("weka.datagenerators")


class DataGenerator(OptionHandler):
    """
    Wrapper class for datagenerators.
    """

    def __init__(self, classname="weka.datagenerators.classifiers.classification.Agrawal", jobject=None, options=None):
        """
        Initializes the specified datagenerator using either the classname or the supplied JB_Object.

        :param classname: the classname of the datagenerator
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        """
        if jobject is None:
            jobject = DataGenerator.new_instance(classname)
        self.enforce_type(jobject, "weka.datagenerators.DataGenerator")
        super(DataGenerator, self).__init__(jobject=jobject, options=options)

    def define_data_format(self):
        """
        Returns the data format.

        :return: the data format
        :rtype: Instances
        """
        data = javabridge.call(self.jobject, "defineDataFormat", "()Lweka/core/Instances;")
        if data is None:
            return None
        else:
            return Instances(data)

    @property
    def single_mode_flag(self):
        """
        Returns whether data is generated row by row (True) or in one go (False).

        :return: whether incremental
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getSingleModeFlag", "()Z")

    @property
    def dataset_format(self):
        """
        Returns the dataset format.

        :return: the format
        :rtype: Instances
        """
        data = javabridge.call(self.jobject, "getDatasetFormat", "()Lweka/core/Instances;")
        if data is None:
            return None
        else:
            return Instances(data)

    @dataset_format.setter
    def dataset_format(self, inst):
        """
        Sets the dataset format.

        :param inst: the Instances to use as dataset format
        :type inst: Instances
        """
        javabridge.call(self.jobject, "setDatasetFormat", "(Lweka/core/Instances;)V", inst.jobject)

    def generate_start(self):
        """
        Returns a "start" string.

        :return: the start comment
        :rtype: str
        """
        return javabridge.call(self.jobject, "generateStart", "()Ljava/lang/String;")

    @property
    def num_examples_act(self):
        """
        Returns a actual number of examples to generate.

        :return: the number of examples
        :rtype: int
        """
        return javabridge.call(self.jobject, "getNumExamplesAct", "()I")

    def generate_example(self):
        """
        Returns a single Instance.

        :return: the next example
        :rtype: Instance
        """
        data = javabridge.call(self.jobject, "generateExample", "()Lweka/core/Instance;")
        if data is None:
            return None
        else:
            return Instance(data)

    def generate_examples(self):
        """
        Returns complete dataset.

        :return: the generated dataset
        :rtype: Instances
        """
        data = javabridge.call(self.jobject, "generateExamples", "()Lweka/core/Instances;")
        if data is None:
            return None
        else:
            return Instances(data)

    def generate_finish(self):
        """
        Returns a "finish" string.

        :return: a finish comment
        :rtype: str
        """
        return javabridge.call(self.jobject, "generateFinish", "()Ljava/lang/String;")

    @classmethod
    def make_data(cls, generator, args):
        """
        Generates data using the generator and commandline arguments.

        :param generator: the generator instance to use
        :type generator: DataGenerator
        :param args: the command-line arguments
        :type args: list
        """
        javabridge.static_call(
            "Lweka/datagenerators/DataGenerator;", "makeData",
            "(Lweka/datagenerators/DataGenerator;[Ljava/lang/String;)V",
            generator.jobject, args)

    @classmethod
    def make_copy(cls, generator):
        """
        Creates a copy of the generator.

        :param generator: the generator to copy
        :type generator: DataGenerator
        :return: the copy of the generator
        :rtype: DataGenerator
        """
        return from_commandline(
            to_commandline(generator), classname=classes.get_classname(DataGenerator()))


def main(args=None):
    """
    Runs a datagenerator from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Executes a data generator from the command-line. Calls JVM start/stop automatically.')
    parser.add_argument("-j", metavar="classpath", dest="classpath", help="additional classpath, jars/directories")
    parser.add_argument("-X", metavar="heap", dest="heap", help="max heap size for jvm, e.g., 512m")
    parser.add_argument("datagenerator", help="data generator classname, e.g., "
                                              + "weka.datagenerators.classifiers.classification.LED24")
    parser.add_argument("option", nargs=argparse.REMAINDER, help="additional data generator options")
    parsed = parser.parse_args(args=args)
    jars = []
    if parsed.classpath is not None:
        jars = parsed.classpath.split(os.pathsep)

    jvm.start(jars, max_heap_size=parsed.heap, packages=True)

    logger.debug("Commandline: " + join_options(sys.argv[1:]))

    try:
        generator = DataGenerator(classname=parsed.datagenerator)
        if len(parsed.option) > 0:
            generator.options = parsed.option
        DataGenerator.make_data(generator, parsed.option)
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
