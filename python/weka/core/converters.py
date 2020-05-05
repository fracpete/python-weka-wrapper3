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

# converters.py
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
from weka.core.classes import OptionHandler
from weka.core.capabilities import Capabilities
from weka.core.dataset import Instances, Instance, Attribute
import numpy
import os


class Loader(OptionHandler):
    """
    Wrapper class for Loaders.
    """
    
    def __init__(self, classname="weka.core.converters.ArffLoader", jobject=None, options=None):
        """
        Initializes the specified loader either using the classname or the JB_Object.

        :param classname: the classname of the loader
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Loader.new_instance(classname)
        self.enforce_type(jobject, "weka.core.converters.Loader")
        super(Loader, self).__init__(jobject=jobject, options=options)
        self.incremental = False
        self.structure = None

    def __iter__(self):
        """
        Returns an iterator in case the loader was instantiated in incremental mode, otherwise
        an Exception is raised.

        :return: the iterator
        :rtype: IncrementalLoaderIterator
        """
        if not self.incremental:
            raise Exception("Not in incremental mode, cannot iterate!")
        return IncrementalLoaderIterator(self, self.structure)

    def load_file(self, dfile, incremental=False, class_index=None):
        """
        Loads the specified file and returns the Instances object.
        In case of incremental loading, only the structure.

        :param dfile: the file to load
        :type dfile: str
        :param incremental: whether to load the dataset incrementally
        :type incremental: bool
        :param class_index: the class index string to use ('first', 'second', 'third', 'last-2', 'last-1', 'last' or 1-based index)
        :type class_index: str
        :return: the full dataset or the header (if incremental)
        :rtype: Instances
        :raises Exception: if the file does not exist
        """
        self.enforce_type(self.jobject, "weka.core.converters.FileSourcedConverter")
        self.incremental = incremental
        if not javabridge.is_instance_of(dfile, "Ljava/io/File;"):
            dfile = javabridge.make_instance(
                "Ljava/io/File;", "(Ljava/lang/String;)V", javabridge.get_env().new_string_utf(str(dfile)))
        javabridge.call(self.jobject, "reset", "()V")
        # check whether file exists, otherwise previously set file gets loaded again
        sfile = javabridge.to_string(dfile)
        if not os.path.exists(sfile):
            raise Exception("Dataset file does not exist: " + str(sfile))
        javabridge.call(self.jobject, "setFile", "(Ljava/io/File;)V", dfile)
        if incremental:
            self.structure = Instances(javabridge.call(self.jobject, "getStructure", "()Lweka/core/Instances;"))
            result = self.structure
        else:
            result = Instances(javabridge.call(self.jobject, "getDataSet", "()Lweka/core/Instances;"))
        if class_index is not None:
            if class_index == 'first':
                result.class_index = 0
            elif class_index == 'second':
                result.class_index = 1
            elif class_index == 'third':
                result.class_index = 2
            elif class_index == 'last-2':
                result.class_index = result.num_attributes - 3
            elif class_index == 'last-1':
                result.class_index = result.num_attributes - 2
            elif class_index == 'last':
                result.class_index = result.num_attributes - 1
            else:
                result.class_index = int(class_index)
        return result
        
    def load_url(self, url, incremental=False):
        """
        Loads the specified URL and returns the Instances object.
        In case of incremental loading, only the structure.

        :param url: the URL to load the data from
        :type url: str
        :param incremental: whether to load the dataset incrementally
        :type incremental: bool
        :return: the full dataset or the header (if incremental)
        :rtype: Instances
        """
        self.enforce_type(self.jobject, "weka.core.converters.URLSourcedLoader")
        self.incremental = incremental
        javabridge.call(self.jobject, "reset", "()V")
        javabridge.call(self.jobject, "setURL", "(Ljava/lang/String;)V", str(url))
        if incremental:
            self.structure = Instances(javabridge.call(self.jobject, "getStructure", "()Lweka/core/Instances;"))
            return self.structure
        else:
            return Instances(javabridge.call(self.jobject, "getDataSet", "()Lweka/core/Instances;"))


class IncrementalLoaderIterator(object):
    """
    Iterator for dataset rows when loarding incrementally.
    """
    def __init__(self, loader, structure):
        """
        :param loader: the loader instance to use for loading the data incrementally
        :type loader: Loader
        :param structure: the dataset structure
        :type structure: Instances
        """
        self.loader = loader
        self.structure = structure

    def __iter__(self):
        """
        Returns itself.
        """
        return self

    def __next__(self):
        """
        Reads the next dataset row.

        :return: the next row
        :rtype: Instance
        """
        result = javabridge.call(
            self.loader.jobject, "getNextInstance",
            "(Lweka/core/Instances;)Lweka/core/Instance;", self.structure.jobject)
        if result is None:
            raise StopIteration()
        else:
            return Instance(result)


class TextDirectoryLoader(OptionHandler):
    """
    Wrapper class for TextDirectoryLoader.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the text directory loader either using a new instance or the JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = TextDirectoryLoader.new_instance("weka.core.converters.TextDirectoryLoader")
        self.enforce_type(jobject, "weka.core.converters.TextDirectoryLoader")
        super(TextDirectoryLoader, self).__init__(jobject=jobject, options=options)

    def load(self):
        """
        Loads the text files from the specified directory and returns the Instances object.
        In case of incremental loading, only the structure.

        :return: the full dataset or the header (if incremental)
        :rtype: Instances
        """
        javabridge.call(self.jobject, "reset", "()V")
        return Instances(javabridge.call(self.jobject, "getDataSet", "()Lweka/core/Instances;"))


class Saver(OptionHandler):
    """
    Wrapper class for Savers.
    """
    
    def __init__(self, classname="weka.core.converters.ArffSaver", jobject=None, options=None):
        """
        Initializes the specified saver either using the classname or the provided JB_Object.

        :param classname: the classname of the saver
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = Saver.new_instance(classname)
        self.enforce_type(jobject, "weka.core.converters.Saver")
        super(Saver, self).__init__(jobject=jobject, options=options)

    def capabilities(self):
        """
        Returns the capabilities of the saver.

        :return: the capabilities
        :rtype: Capabilities
        """
        return Capabilities(javabridge.call(self.jobject, "getCapabilities", "()Lweka/core/Capabilities;"))

    def save_file(self, data, dfile):
        """
        Saves the Instances object in the specified file.

        :param data: the data to save
        :type data: Instances
        :param dfile: the file to save the data to
        :type dfile: str
        """
        self.enforce_type(self.jobject, "weka.core.converters.FileSourcedConverter")
        if not javabridge.is_instance_of(dfile, "Ljava/io/File;"):
            dfile = javabridge.make_instance(
                "Ljava/io/File;", "(Ljava/lang/String;)V", javabridge.get_env().new_string_utf(str(dfile)))
        javabridge.call(self.jobject, "setFile", "(Ljava/io/File;)V", dfile)
        javabridge.call(self.jobject, "setInstances", "(Lweka/core/Instances;)V", data.jobject)
        javabridge.call(self.jobject, "writeBatch", "()V")


def loader_for_file(filename):
    """
    Returns a Loader that can load the specified file, based on the file extension. None if failed to determine.

    :param filename: the filename to get the loader for
    :type filename: str
    :return: the assoicated loader instance or None if none found
    :rtype: Loader
    """
    loader = javabridge.static_call(
        "weka/core/converters/ConverterUtils", "getLoaderForFile",
        "(Ljava/lang/String;)Lweka/core/converters/AbstractFileLoader;", filename)
    if loader is None:
        return None
    else:
        return Loader(jobject=loader)


def load_any_file(filename, class_index=None):
    """
    Determines a Loader based on the the file extension. If successful, loads the full dataset and returns it.

    :param filename: the name of the file to load
    :type filename: str
    :param class_index: the class index string to use ('first', 'second', 'third', 'last-2', 'last-1', 'last' or 1-based index)
    :type class_index: str
    :return: the
    :rtype: Instances
    """
    loader = loader_for_file(filename)
    if loader is None:
        return None
    else:
        return loader.load_file(filename, class_index=class_index)


def saver_for_file(filename):
    """
    Returns a Saver that can load the specified file, based on the file extension. None if failed to determine.

    :param filename: the filename to get the saver for
    :type filename: str
    :return: the associated saver instance or None if none found
    :rtype: Saver
    """
    saver = javabridge.static_call(
        "weka/core/converters/ConverterUtils", "getSaverForFile",
        "(Ljava/lang/String;)Lweka/core/converters/AbstractFileSaver;", filename)
    if saver is None:
        return None
    else:
        return Saver(jobject=saver)


def save_any_file(data, filename):
    """
    Determines a Saver based on the the file extension. Returns whether successfully saved.

    :param filename: the name of the file to save
    :type filename: str
    :param data: the data to save
    :type data: Instances
    :return: whether successfully saved
    :rtype: bool
    """
    saver = saver_for_file(filename)
    if saver is None:
        return False
    else:
        saver.save_file(data, filename)
        return True


def ndarray_to_instances(array, relation, att_template="Att-#", att_list=None):
    """
    Converts the numpy matrix into an Instances object and returns it.

    :param array: the numpy ndarray to convert
    :type array: numpy.darray
    :param relation: the name of the dataset
    :type relation: str
    :param att_template: the prefix to use for the attribute names, "#" is the 1-based index,
                         "!" is the 0-based index, "@" the relation name
    :type att_template: str
    :param att_list: the list of attribute names to use
    :type att_list: list
    :return: the generated instances object
    :rtype: Instances
    """
    if len(numpy.shape(array)) != 2:
        raise Exception("Number of array dimensions must be 2!")
    rows, cols = numpy.shape(array)

    # header
    atts = []
    if att_list is not None:
        if len(att_list) != cols:
            raise Exception(
                "Number columns and provided attribute names differ: " + str(cols) + " != " + len(att_list))
        for name in att_list:
            att = Attribute.create_numeric(name)
            atts.append(att)
    else:
        for i in range(cols):
            name = att_template.replace("#", str(i+1)).replace("!", str(i)).replace("@", relation)
            att = Attribute.create_numeric(name)
            atts.append(att)
    result = Instances.create_instances(relation, atts, rows)

    # data
    for i in range(rows):
        inst = Instance.create_instance(array[i])
        result.add_instance(inst)

    return result
