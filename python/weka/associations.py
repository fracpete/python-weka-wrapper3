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
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import os
import sys
import argparse
import weka.core.jvm as jvm
import weka.core.converters as converters
from weka.core.classes import OptionHandler, join_options
from weka.core.capabilities import Capabilities

# logging setup
logger = logging.getLogger("weka.associations")


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
        super(Associator, self).__init__(jobject=jobject, options=options)

    @property
    def capabilities(self):
        """
        Returns the capabilities of the associator.

        :return: the capabilities
        :rtype: Capabilities
        """
        return Capabilities(javabridge.call(self.jobject, "getCapabilities", "()Lweka/core/Capabilities;"))

    def build_associations(self, data):
        """
        Builds the associator with the data.

        :param data: the data to train the associator with
        :type data: Instances
        """
        javabridge.call(self.jobject, "buildAssociations", "(Lweka/core/Instances;)V", data.jobject)

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


def main():
    """
    Runs a associator from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.
    """

    parser = argparse.ArgumentParser(
        description='Executes an associator from the command-line. Calls JVM start/stop automatically.')
    parser.add_argument("-j", metavar="classpath", dest="classpath", help="additional classpath, jars/directories")
    parser.add_argument("-X", metavar="heap", dest="heap", help="max heap size for jvm, e.g., 512m")
    parser.add_argument("-t", metavar="train", dest="train", required=True, help="training set file")
    parser.add_argument("associator", help="associator classname, e.g., weka.associations.Apriori")
    parser.add_argument("option", nargs=argparse.REMAINDER, help="additional associator options")
    parsed = parser.parse_args()
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
    except Exception as e:
        print(e)
    finally:
        jvm.stop()

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
