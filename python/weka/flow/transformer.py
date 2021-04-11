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

# transformer.py
# Copyright (C) 2015-2016 Fracpete (pythonwekawrapper at gmail dot com)


import os
import re
import javabridge
import math  # required for MathExpression
from weka.associations import Associator
import weka.core.classes as classes
from weka.core.classes import serialization_read, serialization_read_all, deepcopy
import weka.attribute_selection as attsel
import weka.filters as filters
import weka.flow.base as base
from weka.flow.base import InputConsumer, OutputProducer, Token
from weka.flow.container import ModelContainer, AttributeSelectionContainer, ClassificationContainer, ClusteringContainer
import weka.core.converters as converters
from weka.core.dataset import Instances, Instance
from weka.classifiers import Classifier, Evaluation
from weka.clusterers import Clusterer, ClusterEvaluation
from weka.core.classes import Random, is_instance_of
import weka.flow.conversion as conversion


class Transformer(InputConsumer, OutputProducer):
    """
    The ancestor for all sources.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(InputConsumer, self).__init__(name=name, config=config)
        super(OutputProducer, self).__init__(name=name, config=config)

    def post_execute(self):
        """
        Gets executed after the actual execution.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = super(Transformer, self).post_execute()
        if result is None:
            self._input = None
        return result


class PassThrough(Transformer):
    """
    Dummy actor that just passes through the data.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(PassThrough, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Dummy actor that just passes through the data."

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        self._output.append(self.input)


class LoadDataset(Transformer):
    """
    Loads a dataset from a file.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(LoadDataset, self).__init__(name=name, config=config)
        self._loader = None
        self._iterator = None

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Loads a dataset from a file. Either all at once or incrementally."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "incremental: " + str(self.config["incremental"]) \
               + ", custom: " + str(self.config["use_custom_loader"]) \
               + ", loader: " + base.to_commandline(self.config["custom_loader"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        opt = "incremental"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to load the dataset incrementally (bool)."

        opt = "use_custom_loader"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to use a custom loader."

        opt = "custom_loader"
        if opt not in options:
            options[opt] = converters.Loader(classname="weka.core.converters.ArffLoader")
        if opt not in self.help:
            self.help[opt] = "The custom loader to use (Loader)."

        return super(LoadDataset, self).fix_config(options)

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if token is None:
            raise Exception(self.full_name + ": No token provided!")
        if isinstance(token.payload, str):
            return
        raise Exception(self.full_name + ": Unhandled class: " + classes.get_classname(token.payload))

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        fname = str(self.input.payload)
        if not os.path.exists(fname):
            return "File '" + fname + "' does not exist!"
        if not os.path.isfile(fname):
            return "Location '" + fname + "' is not a file!"
        if self.resolve_option("use_custom_loader"):
            self._loader = self.resolve_option("custom_loader")
        else:
            self._loader = converters.loader_for_file(fname)
        dataset = self._loader.load_file(fname, incremental=bool(self.resolve_option("incremental")))
        if not self.resolve_option("incremental"):
            self._output.append(Token(dataset))
        else:
            self._iterator = self._loader.__iter__()
        return None

    def has_output(self):
        """
        Checks whether any output tokens are present.

        :return: true if at least one output token present
        :rtype: bool
        """
        return super(LoadDataset, self).has_output() or (self._iterator is not None)

    def output(self):
        """
        Returns the next available output token.

        :return: the next token, None if none available
        :rtype: Token
        """
        if self._iterator is not None:
            try:
                inst = self._iterator.next()
                result = Token(inst)
            except Exception as e:
                self._iterator = None
                result = None
        else:
            result = super(LoadDataset, self).output()
        return result

    def stop_execution(self):
        """
        Triggers the stopping of the object.
        """
        super(LoadDataset, self).stop_execution()
        self._loader = None
        self._iterator = None

    def wrapup(self):
        """
        Finishes up after execution finishes, does not remove any graphical output.
        """
        self._loader = None
        self._iterator = None
        super(LoadDataset, self).wrapup()


class SetStorageValue(Transformer):
    """
    Store the payload of the current token in internal storage using the specified name.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(SetStorageValue, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Store the payload of the current token in internal storage using the specified name."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "name: " + str(self.config["storage_name"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(SetStorageValue, self).fix_config(options)

        opt = "storage_name"
        if opt not in options:
            options[opt] = "unknown"
        if opt not in self.help:
            self.help[opt] = "The storage value name for storing the payload under (string)."

        return options

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if self.storagehandler is None:
            return "No storage handler available!"
        self.storagehandler.storage[self.resolve_option("storage_name")] = self.input.payload
        self._output.append(self.input)
        return None


class DeleteStorageValue(Transformer):
    """
    Deletes the specified value from internal storage.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(DeleteStorageValue, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Deletes the specified value from internal storage."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "name: " + str(self.config["storage_name"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(DeleteStorageValue, self).fix_config(options)

        opt = "storage_name"
        if opt not in options:
            options[opt] = "unknown"
        if opt not in self.help:
            self.help[opt] = "The name of the storage value to delete (string)."

        return options

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if self.storagehandler is None:
            return "No storage handler available!"
        self.storagehandler.storage.pop(self.resolve_option("storage_name"), None)
        self._output.append(self.input)
        return None


class InitStorageValue(Transformer):
    """
    Initializes the storage value with the provided value (interpreted by 'eval' method).
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(InitStorageValue, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Initializes the storage value with the provided value (interpreted by 'eval' method)."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "name: " + str(self.config["storage_name"]) + ", value: " + str(self.config["value"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(InitStorageValue, self).fix_config(options)

        opt = "storage_name"
        if opt not in options:
            options[opt] = "unknown"
        if opt not in self.help:
            self.help[opt] = "The name of the storage value to delete (string)."

        opt = "value"
        if opt not in options:
            options[opt] = "1"
        if opt not in self.help:
            self.help[opt] = "The initial value (string)."

        return options

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if self.storagehandler is None:
            return "No storage handler available!"
        self.storagehandler.storage[self.resolve_option("storage_name")] = eval(str(self.resolve_option("value")))
        self._output.append(self.input)
        return None


class UpdateStorageValue(Transformer):
    """
    Updates the specified storage value using the epxression interpreted by 'eval' method.
    The current value is available through the variable {X} in the expression.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(UpdateStorageValue, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Updates the specified storage value using the epxression interpreted by 'eval' method.\n"\
               "The current value is available through the variable {X} in the expression.\n"\
               "Any storage value can be referenced using @{name} with 'name' being the name of the storage value."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "name: " + str(self.config["storage_name"]) + ", expression: " + str(self.config["expression"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(UpdateStorageValue, self).fix_config(options)

        opt = "storage_name"
        if opt not in options:
            options[opt] = "unknown"
        if opt not in self.help:
            self.help[opt] = "The name of the storage value to update (string)."

        opt = "expression"
        if opt not in options:
            options[opt] = "int({X} + 1)"
        if opt not in self.help:
            self.help[opt] = "The expression for updating the storage value; use {X} for current value (string)."

        return options

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if self.storagehandler is None:
            return "No storage handler available!"
        expr = str(self.resolve_option("expression")).replace(
            "{X}", str(self.storagehandler.storage[str(self.resolve_option("storage_name"))]))
        expr = self.storagehandler.expand(expr)
        self.storagehandler.storage[self.resolve_option("storage_name")] = eval(expr)
        self._output.append(self.input)
        return None


class MathExpression(Transformer):
    """
    Calculates a mathematical expression. The placeholder {X} in the expression gets replaced by
    the value of the current token passing through. Uses the 'eval(str)' method for the calculation,
    therefore mathematical functions can be accessed using the 'math' library, e.g., '1 + math.sin({X})'.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(MathExpression, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return \
            "Calculates a mathematical expression. The placeholder {X} in the expression gets replaced by "\
            + "the value of the current token passing through. Uses the 'eval(str)' method for the calculation, "\
            + "therefore mathematical functions can be accessed using the 'math' library, e.g., '1 + math.sin({X})'."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "expression: " + str(self.config["expression"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(MathExpression, self).fix_config(options)

        opt = "expression"
        if opt not in options:
            options[opt] = "{X}"
        if opt not in self.help:
            self.help[opt] = "The mathematical expression to evaluate (string)."

        return options

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        expr = str(self.resolve_option("expression"))
        expr = expr.replace("{X}", str(self.input.payload))
        self._output.append(Token(eval(expr)))
        return None


class ClassSelector(Transformer):
    """
    Sets/unsets the class index of a dataset.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(ClassSelector, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Sets/unsets the class index of a dataset."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """

        return "index: " + str(self.config["index"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(ClassSelector, self).fix_config(options)

        opt = "index"
        if opt not in options:
            options[opt] = "last"
        if opt not in self.help:
            self.help[opt] = "The class index (1-based number); 'first' and 'last' are accepted as well (string)."

        opt = "unset"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to unset the class index (bool)."

        return options

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if isinstance(token.payload, Instances):
            return
        if isinstance(token.payload, Instance):
            return
        raise Exception(self.full_name + ": Unhandled data type: " + str(token.payload.__class__.__name__))

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if isinstance(self.input.payload, Instances):
            inst = None
            data = self.input.payload
        elif isinstance(self.input.payload, Instance):
            inst = self.input.payload
            data = inst.dataset

        index = str(self.resolve_option("index"))
        unset = bool(self.resolve_option("unset"))
        if unset:
            data.no_class()
        else:
            if index == "first":
                data.class_is_first()
            elif index == "last":
                data.class_is_last()
            else:
                data.class_index = int(index) - 1

        if inst is None:
            self._output.append(Token(data))
        else:
            self._output.append(Token(inst))

        return None


class Train(Transformer):
    """
    Trains the classifier/clusterer/associator on the incoming dataset and forwards a ModelContainer with the trained
    model and the dataset header.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Train, self).__init__(name=name, config=config)
        self._model = None
        self._header = None

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return \
            "Trains the classifier/clusterer/associator on the incoming dataset and forwards a ModelContainer with the trained " \
            + "model and the dataset header."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "setup: " + base.to_commandline(self.config["setup"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(Train, self).fix_config(options)

        opt = "setup"
        if opt not in options:
            options[opt] = Classifier(classname="weka.classifiers.rules.ZeroR")
        if opt not in self.help:
            self.help[opt] = "The classifier/clusterer/associator to train (Classifier/Clusterer/Associator)."

        return options

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if isinstance(token.payload, Instances):
            return
        if isinstance(token.payload, Instance):
            return
        raise Exception(self.full_name + ": Unhandled data type: " + str(token.payload.__class__.__name__))

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if isinstance(self.input.payload, Instances):
            inst = None
            data = self.input.payload
        else:
            inst = self.input.payload
            data = inst.dataset

        retrain = False
        if (self._header is None) or (self._header.equal_headers(data) is not None) or (inst is None):
            retrain = True
            self._header = Instances.template_instances(data, 0)

        if retrain or (self._model is None):
            cls = self.resolve_option("setup")
            if isinstance(cls, Classifier):
                self._model = Classifier.make_copy(cls)
            elif isinstance(cls, Clusterer):
                self._model = Clusterer.make_copy(cls)
            elif isinstance(cls, Associator):
                self._model = Associator.make_copy(cls)
            else:
                return "Unhandled class: " + classes.get_classname(cls)

        if retrain:
            if inst is not None:
                data = Instances.template_instances(data, 1)
                data.add_instance(inst)
            if isinstance(self._model, Classifier):
                self._model.build_classifier(data)
            elif isinstance(self._model, Clusterer):
                self._model.build_clusterer(data)
            elif isinstance(self._model, Associator):
                self._model.build_associations(data)
        else:
            if isinstance(self._model, Classifier):
                self._model.update_classifier(inst)
            elif isinstance(self._model, Clusterer):
                self._model.update_clusterer(inst)
            else:
                return "Cannot train incrementally: " + classes.get_classname(self._model)

        cont = ModelContainer(model=self._model, header=self._header)
        self._output.append(Token(cont))
        return None


class Filter(Transformer):
    """
    Filters a dataset with the specified filter setup.
    Automatically resets the filter if the dataset differs.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Filter, self).__init__(name=name, config=config)
        self._filter = None
        self._header = None

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Filters a dataset with the specified filter setup.\n"\
               "Automatically resets the filter if the dataset differs."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "setup: " + base.to_commandline(self.config["setup"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        opt = "setup"
        if opt not in options:
            options[opt] = filters.Filter(classname="weka.filters.AllFilter")
        if opt not in self.help:
            self.help[opt] = "The filter to apply to the dataset (Filter)."

        opt = "keep_relationname"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to keep the original relation name (bool)."

        return super(Filter, self).fix_config(options)

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if token is None:
            raise Exception(self.full_name + ": No token provided!")
        if isinstance(token.payload, Instances):
            return
        if isinstance(token.payload, Instance):
            return
        raise Exception(self.full_name + ": Unhandled class: " + classes.get_classname(token.payload))

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if isinstance(self.input.payload, Instance):
            inst = self.input.payload
            data = Instances.template_instances(inst.dataset, 1)
            data.add_instance(inst)
        else:
            inst = None
            data = self.input.payload
        relname = data.relationname
        keep = self.resolve_option("keep_relationname")

        if inst is None:
            if (self._filter is None) or self._header.equal_headers(data) is not None:
                self._header = Instances.template_instances(data)
                self._filter = filters.Filter.make_copy(self.resolve_option("setup"))
                self._filter.inputformat(data)
            filtered = self._filter.filter(data)
            if keep:
                filtered.relationname = relname
            self._output.append(Token(filtered))
        else:
            if (self._filter is None) or self._header.equal_headers(data) is not None:
                self._header = Instances.template_instances(data)
                self._filter = filters.Filter.make_copy(self.resolve_option("setup"))
                self._filter.inputformat(data)
                filtered = self._filter.filter(data)
                if keep:
                    filtered.relationname = relname
                self._output.append(Token(filtered.get_instance(0)))
            else:
                self._filter.input(inst)
                self._filter.batch_finished()
                filtered = self._filter.output()
                if keep:
                    filtered.dataset.relationname = relname
                self._output.append(Token(filtered))

        return None


class DeleteFile(Transformer):
    """
    Deletes the incoming files that match the regular expression.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(DeleteFile, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Deletes the incoming files that match the regular expression."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "regexp: " + str(self.config["regexp"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(DeleteFile, self).fix_config(options)

        opt = "regexp"
        if opt not in options:
            options[opt] = ".*"
        if opt not in self.help:
            self.help[opt] = "The regular expression that the files must match (string)."

        return options

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        fname = str(self.input.payload)
        spattern = str(self.resolve_option("regexp"))
        pattern = None
        if (spattern is not None) and (spattern != ".*"):
            pattern = re.compile(spattern)
        if (pattern is None) or (pattern.match(fname)):
            os.remove(fname)
        self._output.append(self.input)
        return None


class CrossValidate(Transformer):
    """
    Cross-validates the classifier/clusterer on the incoming dataset. In case of a classifier, the Evaluation object
    is forwarded. For clusterers the loglikelihood.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(CrossValidate, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Cross-validates the classifier/clusterer on the incoming dataset. In case of a classifier, the "\
               "Evaluation object is forwarded. For clusterers the loglikelihood."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "setup: " + base.to_commandline(self.config["setup"]) + ", folds: " + str(self.config["folds"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(CrossValidate, self).fix_config(options)

        opt = "setup"
        if opt not in options:
            options[opt] = Classifier(classname="weka.classifiers.rules.ZeroR")
        if opt not in self.help:
            self.help[opt] = "The classifier/clusterer to train (Classifier/Clusterer)."

        opt = "folds"
        if opt not in options:
            options[opt] = 10
        if opt not in self.help:
            self.help[opt] = "The number of folds for CV (int)."

        opt = "seed"
        if opt not in options:
            options[opt] = 1
        if opt not in self.help:
            self.help[opt] = "The seed value for randomizing the data (int)."

        opt = "discard_predictions"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Discard classifier predictions to save memory (bool)."

        opt = "output"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "For capturing the classifier's prediction output (PredictionOutput)."

        return options

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if isinstance(token.payload, Instances):
            return
        raise Exception(self.full_name + ": Unhandled data type: " + str(token.payload.__class__.__name__))

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        data = self.input.payload
        cls = self.resolve_option("setup")
        if isinstance(cls, Classifier):
            cls = Classifier.make_copy(cls)
            evl = Evaluation(data)
            evl.discard_predictions = bool(self.resolve_option("discard_predictions"))
            evl.crossvalidate_model(
                cls,
                data,
                int(self.resolve_option("folds")),
                Random(int(self.resolve_option("seed"))),
                self.resolve_option("output"))
            self._output.append(Token(evl))
        elif isinstance(cls, Clusterer):
            cls = Clusterer.make_copy(cls)
            evl = ClusterEvaluation()
            llh = evl.crossvalidate_model(
                cls,
                data,
                int(self.resolve_option("folds")),
                Random(int(self.resolve_option("seed"))))
            self._output.append(Token(llh))
        else:
            return "Unhandled class: " + classes.get_classname(cls)
        return None


class Evaluate(Transformer):
    """
    Evaluates a trained classifier obtained from internal storage on the dataset passing through.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Evaluate, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Evaluates a trained classifier obtained from internal storage on the dataset passing through."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "storage: " + self.config["storage_name"]

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(Evaluate, self).fix_config(options)

        opt = "storage_name"
        if opt not in options:
            options[opt] = "unknown"
        if opt not in self.help:
            self.help[opt] = "The name of the classifier model in storage (string)."

        opt = "discard_predictions"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Discard classifier predictions to save memory (bool)."

        opt = "output"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "For capturing the classifier's prediction output (PredictionOutput)."

        return options

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if isinstance(token.payload, Instances):
            return
        raise Exception(self.full_name + ": Unhandled data type: " + str(token.payload.__class__.__name__))

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        data = self.input.payload
        if self.storagehandler is None:
            return "No storage handler available!"
        sname = str(self.resolve_option("storage_name"))
        if sname not in self.storagehandler.storage:
            return "No storage item called '" + sname + "' present!"
        cls = self.storagehandler.storage[sname]
        if isinstance(cls, Classifier):
            evl = Evaluation(data)
            evl.discard_predictions = bool(self.resolve_option("discard_predictions"))
            evl.test_model(
                cls,
                data,
                self.resolve_option("output"))
        elif isinstance(cls, Clusterer):
            evl = ClusterEvaluation()
            evl.set_model(cls)
            evl.test_model(data)
        else:
            return "Unhandled class: " + classes.get_classname(cls)
        self._output.append(Token(evl))
        return None


class EvaluationSummary(Transformer):
    """
    Generates a summary string from an Evaluation/ClusterEvaluation object.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(EvaluationSummary, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Generates a summary string from an Evaluation object."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "title: " + str(self.config["title"]) \
               + ", complexity: " + str(self.config["complexity"]) \
               + ", matrix: " + str(self.config["matrix"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(EvaluationSummary, self).fix_config(options)

        opt = "title"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The title for the output (string)."

        opt = "complexity"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to output classifier complexity information (bool)."

        opt = "matrix"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to output the classifier confusion matrix (bool)."

        return options

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if isinstance(token.payload, Evaluation):
            return None
        if isinstance(token.payload, ClusterEvaluation):
            return None
        raise Exception(
            self.full_name + ": Input token is not a supported Evaluation object - "
            + classes.get_classname(token.payload))

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        evl = self.input.payload
        if isinstance(evl, Evaluation):
            summary = evl.summary(title=self.resolve_option("title"), complexity=bool(self.resolve_option("complexity")))
            if bool(self.resolve_option("matrix")):
                summary += "\n" + evl.matrix(title=self.resolve_option("title"))
        else:
            summary = evl.cluster_results
        self._output.append(Token(summary))
        return None


class ModelReader(Transformer):
    """
    Reads the serialized model (Classifier/Clusterer) from disk and forwards a ModelContainer.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(ModelReader, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Reads the serialized model from disk and forwards a ModelContainer."

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        fname = self.input.payload
        data = serialization_read_all(fname)
        if len(data) == 1:
            if is_instance_of(data[0], "weka.classifiers.Classifier"):
                cont = ModelContainer(model=Classifier(jobject=data[0]))
            elif is_instance_of(data[0], "weka.clusterers.Clusterer"):
                cont = ModelContainer(model=Clusterer(jobject=data[0]))
            else:
                return "Unhandled class: " + classes.get_classname(data[0])
        elif len(data) == 2:
            if is_instance_of(data[0], "weka.classifiers.Classifier"):
                cont = ModelContainer(model=Classifier(jobject=data[0]), header=Instances(data[1]))
            elif is_instance_of(data[0], "weka.clusterers.Clusterer"):
                cont = ModelContainer(model=Clusterer(jobject=data[0]), header=Instances(data[1]))
            else:
                return "Unhandled class: " + classes.get_classname(data[0])
        else:
            return "Expected 1 or 2 objects, but got " + str(len(data)) + " instead reading: " + fname
        self._output.append(Token(cont))
        return None


class Convert(Transformer):
    """
    Converts the input data with the given conversion setup.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Convert, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Converts the input data with the given conversion setup."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "setup: " + str(self.config["setup"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        opt = "setup"
        if opt not in options:
            options[opt] = conversion.PassThrough()
        if opt not in self.help:
            self.help[opt] = "The conversion to apply to the input data (Conversion)."

        return super(Convert, self).fix_config(options)

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if token is None:
            raise Exception(self.full_name + ": No token provided!")
        self.config["setup"].check_input(token.payload)

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        conv = self.config["setup"].shallow_copy()
        conv.input = self._input.payload
        result = conv.convert()
        if result is None:
            if conv.output is not None:
                self._output.append(Token(conv.output))
        return None


class AttributeSelection(Transformer):
    """
    Performs attribute selection on the incoming dataset using the specified search and evaluation scheme.
    Outputs a AttributeSelectionContainer with the results string, reduced dataset and seleted attributes.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(AttributeSelection, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return \
            "Performs attribute selection on the incoming dataset using the specified search and evaluation scheme.\n" \
            "Outputs a AttributeSelectionContainer with the results string, reduced dataset and seleted attributes."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "search: " + base.to_commandline(self.config["search"]) + ", eval: " \
               + base.to_commandline(self.config["eval"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        opt = "search"
        if opt not in options:
            options[opt] = attsel.ASSearch(classname="weka.attributeSelection.BestFirst")
        if opt not in self.help:
            self.help[opt] = "The search algorithm to use (ASSearch)."

        opt = "eval"
        if opt not in options:
            options[opt] = attsel.ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval")
        if opt not in self.help:
            self.help[opt] = "The evaluation algorithm to use (ASEvaluation)."

        return super(AttributeSelection, self).fix_config(options)

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if token is None:
            raise Exception(self.full_name + ": No token provided!")
        if not isinstance(token.payload, Instances):
            raise Exception(self.full_name + ": Not an Instances object!")

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        data = self.input.payload
        search = self.config["search"].shallow_copy()
        evl = self.config["eval"].shallow_copy()
        asel = attsel.AttributeSelection()
        asel.search(search)
        asel.evaluator(evl)
        asel.select_attributes(data)
        cont = AttributeSelectionContainer(
            original=data,
            reduced=asel.reduce_dimensionality(data),
            num_atts=asel.number_attributes_selected,
            selected=asel.selected_attributes,
            results=asel.results_string)
        self._output.append(Token(cont))
        return None


class RenameRelation(Transformer):
    """
    Updates the relation name of Instance/Instances objects passing through.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(RenameRelation, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Updates the relation name of Instance/Instances objects passing through."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "name: " + str(self.config["name"])

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(RenameRelation, self).fix_config(options)

        opt = "name"
        if opt not in options:
            options[opt] = "newname"
        if opt not in self.help:
            self.help[opt] = "The new relation name to use (string)."

        return options

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
        relname = self.resolve_option("name")
        if isinstance(self.input.payload, Instance):
            self.input.payload.dataset.relationname = relname
        else:
            self.input.payload.relationname = relname
        self._output.append(self.input)
        return None


class Copy(Transformer):
    """
    Creates a deep copy of the token passing through (must be a serializable JavaObject),
    other objects just get passed on.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Copy, self).__init__(name=name, config=config)

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return "Creates a deep copy of the token passing through (must be a serializable JavaObject), "\
               "other objects just get passed on."

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if isinstance(self.input.payload, classes.JavaObject) and self.input.payload.is_serializable:
            copy = deepcopy(self.input.payload)
            if copy is not None:
                self._output.append(Token(copy))
        else:
            self._output.append(self.input)
        return None


class Predict(Transformer):
    """
    Uses the serialized model or, if pointing to a directory, the specified model from storage for
    making a prediction on the incoming Instance object. The model can be either a Classifier or Clusterer.
    Outputs either a ClassificationContainer or ClusteringContainer.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the transformer.

        :param name: the name of the transformer
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Predict, self).__init__(name=name, config=config)
        self._model = None
        self._is_classifier = None

    def description(self):
        """
        Returns a description of the actor.

        :return: the description
        :rtype: str
        """
        return \
            "Uses the serialized model or, if pointing to a directory, the specified model from storage for "\
            "making a prediction on the incoming Instance object. The model can be either a Classifier or Clusterer.\n"\
            "Outputs either a ClassificationContainer or ClusteringContainer."

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return "model: " + self.config["model"] + ", storage: " + self.config["storage_name"]

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(Predict, self).fix_config(options)

        opt = "model"
        if opt not in options:
            options[opt] = "."
        if opt not in self.help:
            self.help[opt] = "The serialized model to use for making predictions (string)."

        opt = "storage_name"
        if opt not in options:
            options[opt] = "unknown"
        if opt not in self.help:
            self.help[opt] = "The name of the model (or ModelContainer) in storage to use (string)."

        return options

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        if isinstance(token.payload, Instance):
            return
        raise Exception(self.full_name + ": Unhandled data type: " + str(token.payload.__class__.__name__))

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        inst = self.input.payload
        if not inst.has_class:
            return "No class set!"

        # load model?
        if self._model is None:
            model = None
            fname = str(self.resolve_option("model"))
            if os.path.isfile(fname):
                model = serialization_read(fname)
            else:
                name = self.resolve_option("storage_name")
                if name in self.storagehandler.storage:
                    model = self.storagehandler.storage.get(name)
                    if isinstance(model, ModelContainer):
                        model = model.get("Model").jobject
            if model is None:
                return "No model available from storage or serialized file!"
            self._is_classifier = is_instance_of(model, "weka.classifiers.Classifier")
            if self._is_classifier:
                self._model = Classifier(jobject=model)
            else:
                self._model = Clusterer(jobject=model)

        if self._is_classifier:
            cls = self._model.classify_instance(inst)
            dist = self._model.distribution_for_instance(inst)
            label = inst.class_attribute.value(int(cls))
            cont = ClassificationContainer(inst=inst, classification=cls, distribution=dist, label=label)
        else:
            cls = self._model.cluster_instance(inst)
            dist = self._model.distribution_for_instance(inst)
            cont = ClusteringContainer(inst=inst, cluster=int(cls), distribution=dist)

        self._output.append(Token(cont))
        return None
