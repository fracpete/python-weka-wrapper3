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

# sink.py
# Copyright (C) 2015-2021 Fracpete (pythonwekawrapper at gmail dot com)


import traceback
from weka.core.classes import serialization_write_all
from weka.core.dataset import Instances, Instance
from weka.flow.base import InputConsumer
from weka.flow.container import ModelContainer
from weka.classifiers import Evaluation
import weka.plot.classifiers as pltclassifier
import weka.plot.clusterers as pltclusterer
import weka.plot.dataset as pltdataset


class Sink(InputConsumer):
    """
    The ancestor for all sinks.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Sink, self).__init__(name=name, config=config)
        super(InputConsumer, self).__init__(name=name, config=config)

    def post_execute(self):
        """
        Gets executed after the actual execution.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = super(Sink, self).post_execute()
        if result is None:
            self._input = None
        return result


class Null(Sink):
    """
    Sink that just gobbles up all the data.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Null, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Sink that just gobbles up all the data."

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        return None


class Console(Sink):
    """
    Sink that outputs the payloads of the data on stdout.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Console, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Sink that outputs the payloads of the data on stdout."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "prefix: '" + str(self.config["prefix"]) + "'"

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(Console, self).fix_config(options)

        opt = "prefix"
        if opt not in options:
            options[opt] = ""
        if opt not in self.help:
            self.help[opt] = "The prefix for the output (string)."

        return options

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        print(self.resolve_option("prefix") + str(self.input.payload))
        return None


class FileOutputSink(Sink):
    """
    Ancestor for sinks that output data to a file.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(FileOutputSink, self).__init__(name=name, config=config)

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "output: '" + str(self.config["output"]) + "'"

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(FileOutputSink, self).fix_config(options)

        opt = "output"
        if opt not in options:
            options[opt] = "."
        if opt not in self.help:
            self.help[opt] = "The file to write to (string)."

        return options


class DumpFile(FileOutputSink):
    """
    Sink that outputs the payloads of the data to a file.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(DumpFile, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Sink that outputs the payloads of the data to a file."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return super(DumpFile, self).quickinfo + ", append: " + str(self.config["append"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(DumpFile, self).fix_config(options)

        opt = "append"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to append to the file or overwrite (bool)."

        return options

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = None
        f = None
        try:
            if bool(self.resolve_option("append")):
                f = open(str(self.resolve_option("output")), "a")
            else:
                f = open(str(self.resolve_option("output")), "w")
            f.write(str(self.input.payload))
            f.write("\n")
        except Exception as e:
            result = self.full_name + "\n" + traceback.format_exc()
        finally:
            if f is not None:
                f.close()
        return result


class ModelWriter(FileOutputSink):
    """
    Writes a model to disk.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(ModelWriter, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Writes a model to disk."

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if not isinstance(token.payload, ModelContainer):
            raise Exception(self.full_name + ": Input token is not a ModelContainer!")

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = None
        cont = self.input.payload
        serialization_write_all(
            str(self.resolve_option("output")),
            [cont.get("Model").jobject, cont.get("Header").jobject])
        return result


class MatrixPlot(Sink):
    """
    Displays the Instances object as matrix plot.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(MatrixPlot, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Displays the Instances object as matrix plot."

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(MatrixPlot, self).fix_config(options)

        opt = "percent"
        if opt not in options:
            options[opt] = 100.0
        if opt not in self.help:
            self.help[opt] = "The percentage of the data to display (0-100, float)."

        opt = "seed"
        if opt not in options:
            options[opt] = 1
        if opt not in self.help:
            self.help[opt] = "The seed value for randomizing the plot when viewing a subset (int)."

        opt = "size"
        if opt not in options:
            options[opt] = 10
        if opt not in self.help:
            self.help[opt] = "The size of the circles in the plot (int)."

        opt = "title"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The title for the plot (str)."

        opt = "outfile"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The file to store the plot in (str)."

        opt = "wait"
        if opt not in options:
            options[opt] = True
        if opt not in self.help:
            self.help[opt] = "Whether to wait for user to close the plot window (bool)."

        return options

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "percent: " + str(self.config["percent"]) \
               + ", title: " + str(self.config["title"]) \
               + ", outfile: " + str(self.config["outfile"]) \
               + ", wait: " + str(self.config["wait"])

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if not isinstance(token.payload, Instances):
            raise Exception(self.full_name + ": Input token is not an Instances object!")

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = None
        data = self.input.payload
        pltdataset.matrix_plot(
            data,
            percent=float(self.resolve_option("percent")),
            seed=int(self.resolve_option("seed")),
            size=int(self.resolve_option("size")),
            title=self.resolve_option("title"),
            outfile=self.resolve_option("outfile"),
            wait=bool(self.resolve_option("wait")))
        return result


class LinePlot(Sink):
    """
    Displays the Instances object as line plot using the internal format, one line per Instance.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(LinePlot, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Displays the Instances object as line plot using the internal format, one line per Instance."

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(LinePlot, self).fix_config(options)

        opt = "attributes"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The list of 0-based attribute indices to print; None for all (int)."

        opt = "percent"
        if opt not in options:
            options[opt] = 100.0
        if opt not in self.help:
            self.help[opt] = "The percentage of the data to display (0-100, float)."

        opt = "seed"
        if opt not in options:
            options[opt] = 1
        if opt not in self.help:
            self.help[opt] = "The seed value for randomizing the plot when viewing a subset (int)."

        opt = "title"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The title for the plot (str)."

        opt = "outfile"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The file to store the plot in (str)."

        opt = "wait"
        if opt not in options:
            options[opt] = True
        if opt not in self.help:
            self.help[opt] = "Whether to wait for user to close the plot window (bool)."

        return options

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "percent: " + str(self.config["percent"]) \
               + ", title: " + str(self.config["title"]) \
               + ", outfile: " + str(self.config["outfile"]) \
               + ", wait: " + str(self.config["wait"])

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if not isinstance(token.payload, Instances):
            raise Exception(self.full_name + ": Input token is not an Instances object!")

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = None
        data = self.input.payload
        pltdataset.line_plot(
            data,
            atts=self.resolve_option("attributes"),
            percent=float(self.resolve_option("percent")),
            seed=int(self.resolve_option("seed")),
            title=self.resolve_option("title"),
            outfile=self.resolve_option("outfile"),
            wait=bool(self.resolve_option("wait")))
        return result


class ClassifierErrors(Sink):
    """
    Displays the errors obtained through a classifier evaluation.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(ClassifierErrors, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Displays the errors obtained through a classifier evaluation."

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(ClassifierErrors, self).fix_config(options)

        opt = "absolute"
        if opt not in options:
            options[opt] = True
        if opt not in self.help:
            self.help[opt] = "Whether to use absolute errors as size or relative ones (bool)."

        opt = "max_relative_size"
        if opt not in options:
            options[opt] = 50
        if opt not in self.help:
            self.help[opt] = "The maximum size in point in case of relative mode (int)."

        opt = "absolute_size"
        if opt not in options:
            options[opt] = 50
        if opt not in self.help:
            self.help[opt] = "The size in point in case of absolute mode (int)."

        opt = "title"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The title for the plot (str)."

        opt = "outfile"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The file to store the plot in (str)."

        opt = "wait"
        if opt not in options:
            options[opt] = True
        if opt not in self.help:
            self.help[opt] = "Whether to wait for user to close the plot window (bool)."

        return options

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "absolute: " + str(self.config["absolute"]) \
               + ", title: " + str(self.config["title"]) \
               + ", outfile: " + str(self.config["outfile"]) \
               + ", wait: " + str(self.config["wait"])

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if not isinstance(token.payload, Evaluation):
            raise Exception(self.full_name + ": Input token is not an Evaluation object!")

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = None
        evl = self.input.payload
        pltclassifier.plot_classifier_errors(
            evl.predictions,
            absolute=bool(self.resolve_option("absolute")),
            max_relative_size=int(self.resolve_option("max_relative_size")),
            absolute_size=int(self.resolve_option("absolute_size")),
            title=self.resolve_option("title"),
            outfile=self.resolve_option("outfile"),
            wait=bool(self.resolve_option("wait")))
        return result


class ROC(Sink):
    """
    Displays the ROC curve obtained from a classifier evaluation.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(ROC, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Displays the ROC curve obtained from a classifier evaluation."

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(ROC, self).fix_config(options)

        opt = "class_index"
        if opt not in options:
            options[opt] = [0]
        if opt not in self.help:
            self.help[opt] = "The list of 0-based class-label indices to display (list)."

        opt = "key_loc"
        if opt not in options:
            options[opt] = "lower right"
        if opt not in self.help:
            self.help[opt] = "The location of the key in the plot (str)."

        opt = "title"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The title for the plot (str)."

        opt = "outfile"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The file to store the plot in (str)."

        opt = "wait"
        if opt not in options:
            options[opt] = True
        if opt not in self.help:
            self.help[opt] = "Whether to wait for user to close the plot window (bool)."

        return options

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "classes: " + str(self.config["class_index"]) \
               + ", title: " + str(self.config["title"]) \
               + ", outfile: " + str(self.config["outfile"]) \
               + ", wait: " + str(self.config["wait"])

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if not isinstance(token.payload, Evaluation):
            raise Exception(self.full_name + ": Input token is not an Evaluation object!")

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = None
        evl = self.input.payload
        pltclassifier.plot_roc(
            evl,
            class_index=self.resolve_option("class_index"),
            title=self.resolve_option("title"),
            key_loc=self.resolve_option("key_loc"),
            outfile=self.resolve_option("outfile"),
            wait=bool(self.resolve_option("wait")))
        return result


class PRC(Sink):
    """
    Displays the PRC curve obtained from a classifier evaluation.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(PRC, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Displays the PRC curve obtained from a classifier evaluation."

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(PRC, self).fix_config(options)

        opt = "class_index"
        if opt not in options:
            options[opt] = [0]
        if opt not in self.help:
            self.help[opt] = "The list of 0-based class-label indices to display (list)."

        opt = "key_loc"
        if opt not in options:
            options[opt] = "lower center"
        if opt not in self.help:
            self.help[opt] = "The location of the key in the plot (str)."

        opt = "title"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The title for the plot (str)."

        opt = "outfile"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The file to store the plot in (str)."

        opt = "wait"
        if opt not in options:
            options[opt] = True
        if opt not in self.help:
            self.help[opt] = "Whether to wait for user to close the plot window (bool)."

        return options

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "classes: " + str(self.config["class_index"]) \
               + ", title: " + str(self.config["title"]) \
               + ", outfile: " + str(self.config["outfile"]) \
               + ", wait: " + str(self.config["wait"])

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if not isinstance(token.payload, Evaluation):
            raise Exception(self.full_name + ": Input token is not an Evaluation object!")

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = None
        evl = self.input.payload
        pltclassifier.plot_prc(
            evl,
            class_index=self.resolve_option("class_index"),
            title=self.resolve_option("title"),
            key_loc=self.resolve_option("key_loc"),
            outfile=self.resolve_option("outfile"),
            wait=bool(self.resolve_option("wait")))
        return result


class InstanceDumper(FileOutputSink):
    """
    Sink that dumps the incoming Instance/Instances into a file.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the sink.

        :param name: the name of the sink
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(InstanceDumper, self).__init__(name=name, config=config)
        self._header = None

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Sink that dumps the incoming Instance/Instances objects in a file."

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if isinstance(token.payload, Instance):
            return
        if isinstance(token.payload, Instances):
            return
        raise Exception(self.full_name + ": Input token is neither an Instance nor Instances object!")

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = None

        data = self.input.payload
        if isinstance(self._input.payload, Instance):
            inst = self.input.payload
            data = inst.dataset
        elif isinstance(self.input.payload, Instances):
            data = self.input.payload
            inst = None

        append = True
        if self._header is None or (self._header.equal_headers(data) is not None):
            self._header = Instances.template_instances(data, 0)
            outstr = str(data)
            append = False
        elif inst is not None:
            outstr = str(inst)
        else:
            outstr = str(data)

        f = None
        try:
            if append:
                f = open(str(self.resolve_option("output")), "a")
            else:
                f = open(str(self.resolve_option("output")), "w")
            f.write(outstr)
            f.write("\n")
        except Exception as e:
            result = self.full_name + "\n" + traceback.format_exc()
        finally:
            if f is not None:
                f.close()
        return result
