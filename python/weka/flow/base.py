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

# base.py
# Copyright (C) 2015-2016 Fracpete (pythonwekawrapper at gmail dot com)


import logging
import re
import traceback
import uuid
from weka.core.classes import Configurable, Stoppable
import weka.core.classes as classes


class Actor(Configurable, Stoppable):
    """
    The ancestor for all actors.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the actor.

        :param name: the name of the actor
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(Actor, self).__init__(config=config)
        self._name = self.__class__.__name__
        self._parent = None
        self._full_name = None
        self._stopped = False
        if name is not None:
            self.name = name
        if not classes.has_dict_handler("Actor"):
            classes.register_dict_handler("Actor", Actor.from_dict)

    def __str__(self):
        """
        Returns a short representation of the actor's setup.

        :return: the setup
        :rtype: str
        """
        return self.full_name + ": " + str(self._config)

    def __repr__(self):
        """
        Returns Python code for instantiating the object.

        :return: the representation
        :rtype: str
        """
        return \
            self.__class__.__module__ + "." + self.__class__.__name__ \
            + "(name=" + self.name + ", config=" + str(self.config) + ")"

    def new_logger(self):
        """
        Returns a new logger instance.

        :return: the logger instance
        :rtype: logger
        """
        return logging.getLogger(self.full_name)

    @property
    def name(self):
        """
        Obtains the currently set name of the actor.

        :return: the name
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of the actor.

        :param name: the name
        :type name: str
        """
        self._name = name

    def unique_name(self, name):
        """
        Generates a unique name.

        :param name: the name to check
        :type name: str
        :return: the unique name
        :rtype: str
        """
        result = name

        if self.parent is not None:
            index = self.index
            bname = re.sub(r'-[0-9]+$', '', name)
            names = []
            for idx, actor in enumerate(self.parent.actors):
                if idx != index:
                    names.append(actor.name)
            result = bname
            count = 0
            while result in names:
                count += 1
                result = bname + "-" + str(count)

        return result

    @property
    def parent(self):
        """
        Obtains the currently set parent of the actor.

        :return: the name
        :rtype: str
        """
        return self._parent

    @parent.setter
    def parent(self, parent):
        """
        Sets the parent of the actor.

        :param parent: the parent
        :type parent: Actor
        """
        self._name = self.unique_name(self._name)
        self._full_name = None
        self._logger = None
        self._parent = parent

    @property
    def index(self):
        """
        Returns the index of this actor in its parent's list of actors.

        :return: the index, -1 if not available
        :rtype: int
        """
        if self.parent is None:
            return -1
        else:
            return self.parent.index_of(self.name)

    @property
    def full_name(self):
        """
        Obtains the full name of the actor.

        :return: the full name
        :rtype: str
        """
        if self._full_name is None:
            fn = self.name.replace(".", "\\.")
            parent = self._parent
            if parent is not None:
                fn = parent.full_name + "." + fn
            self._full_name = fn

        return self._full_name

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        opt = "annotation"
        if opt not in options:
            options[opt] = None
        if opt not in self.help:
            self.help[opt] = "The (optional) annotation for this actor (string)."

        opt = "skip"
        if opt not in options:
            options[opt] = False
        if opt not in self.help:
            self.help[opt] = "Whether to skip (disable) this actor (bool)."

        return super(Actor, self).fix_config(options)

    def to_dict(self):
        """
        Returns a dictionary that represents this object, to be used for JSONification.

        :return: the object dictionary
        :rtype: dict
        """
        result = super(Actor, self).to_dict()
        result["type"] = "Actor"
        result["name"] = self.name
        return result

    @classmethod
    def from_dict(cls, d):
        """
        Restores an object state from a dictionary, used in de-JSONification.

        :param d: the object dictionary
        :type d: dict
        :return: the object
        :rtype: object
        """
        conf = {}
        for k in d["config"]:
            v = d["config"][k]
            if isinstance(v, dict):
                if u"type" in v:
                    typestr = v[u"type"]
                else:
                    typestr = v["type"]
                conf[str(k)] = classes.get_dict_handler(typestr)(v)
            else:
                conf[str(k)] = v
        return classes.get_class(d["class"])(name=d["name"], config=conf)

    def resolve_option(self, name, default=None):
        """
        Resolves the option, i.e., interprets "@{...}" values and retrievs them instead from internal
        storage.

        :param name: the name of the option
        :type name: str
        :param default: the optional default value
        :type default: object
        :return: the resolved value
        :rtype: object
        """
        value = self.config[name]
        if value is None:
            return default
        elif isinstance(value, str) \
                and value.startswith("@{") \
                and value.endswith("}") \
                and (value.find("@{", 1) == -1):
            stname = value[2:len(value)-1]
            if (self.storagehandler is not None) and (stname in self.storagehandler.storage):
                return self.storagehandler.storage[stname]
            else:
                return default
        else:
            return value

    @property
    def skip(self):
        """
        Obtains whether the actor is disabled (skipped).

        :return: True if skipped
        :rtype: bool
        """
        return self.resolve_option("skip")

    @skip.setter
    def skip(self, skip):
        """
        Sets whether the actor is skipped.

        :param skip: True if skipped
        :type skip: bool
        """
        self.config["skip"] = skip

    @property
    def quickinfo(self):
        """
        Returns a short string describing some of the options of the actor.

        :return: the info, None if not available
        :rtype: str
        """
        return None

    @property
    def storagehandler(self):
        """
        Returns the storage handler available to thise actor.

        :return: the storage handler, None if not available
        """
        if isinstance(self, StorageHandler):
            return self
        elif self.parent is not None:
            return self.parent.storagehandler
        else:
            return None

    @property
    def root(self):
        """
        Returns the top-level actor.

        :return: the top-level actor
        :rtype: Actor
        """
        if self.parent is None:
            return self
        else:
            return self.parent.root

    @property
    def depth(self):
        """
        Returns the depth of this actor inside the overall flow.

        :return: the depth
        :rtype: int
        """
        if self.parent is None:
            return 0
        else:
            return self.parent.depth + 1

    def is_stopped(self):
        """
        Returns whether the object has been stopped.

        :return: whether stopped
        :rtype: bool
        """
        return self._stopped

    def stop_execution(self):
        """
        Triggers the stopping of the actor.
        """
        self._stopped = True

    def setup(self):
        """
        Configures the actor before execution.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        return None

    def pre_execute(self):
        """
        Gets executed before the actual execution.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        return None

    def do_execute(self):
        """
        The actual execution of the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        raise Exception("Not implemented!")

    def post_execute(self):
        """
        Gets executed after the actual execution.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        return None

    def execute(self):
        """
        Executes the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if self.skip:
            return None

        result = self.pre_execute()
        if result is None:
            try:
                result = self.do_execute()
            except Exception as e:
                result = traceback.format_exc()
                print(self.full_name + "\n" + result)
        if result is None:
            result = self.post_execute()
        return result

    def wrapup(self):
        """
        Finishes up after execution finishes, does not remove any graphical output.
        """
        pass

    def cleanup(self):
        """
        Destructive finishing up after execution stopped.
        """
        pass


class Token(object):
    """
    Container for transporting data through the flow.
    """

    def __init__(self, payload):
        """
        Initializes the token with the given payload.

        :param payload: the payload for the token.
        :type payload: object
        """
        self._id = str(uuid.uuid4())
        self._payload = payload

    @property
    def id(self):
        """
        Obtains the ID of the token.

        :return: the ID
        :rtype: str
        """
        return self._id

    @property
    def payload(self):
        """
        Obtains the currently set payload.

        :return: the payload
        :rtype: object
        """
        return self._payload

    def __str__(self):
        """
        Returns a short representation of the token and its payload.
        """
        return self._id + ": " + str(self._payload)


class InputConsumer(Actor):
    """
    Actors that consume tokens inherit this class.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the actor.

        :param name: the name of the actor
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(InputConsumer, self).__init__(name=name, config=config)
        self._input = None

    def check_input(self, token):
        """
        Performs checks on the input token. Raises an exception if unsupported.

        :param token: the token to check
        :type token: Token
        """
        pass

    @property
    def input(self):
        """
        Returns the current input token, None if not available.

        :return: the input token
        :rtype: Token
        """
        return self._input

    @input.setter
    def input(self, token):
        """
        Accepts the data for processing.

        :param token: the token to process
        :type token: Token
        """
        self.check_input(token)
        self._input = token


class OutputProducer(Actor):
    """
    Actors that generate output tokens inherit this class.
    """

    def __init__(self, name=None, config=None):
        """
        Initializes the actor.

        :param name: the name of the actor
        :type name: str
        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        super(OutputProducer, self).__init__(name=name, config=config)
        self._output = None

    def pre_execute(self):
        """
        Gets executed before the actual execution.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        self._output = []
        return None

    def has_output(self):
        """
        Checks whether any output tokens are present.

        :return: true if at least one output token present
        :rtype: bool
        """
        return (self._output is not None) and (len(self._output) > 0)

    def output(self):
        """
        Returns the next available output token.

        :return: the next token, None if none available
        :rtype: Token
        """
        if (self._output is None) or (len(self._output) == 0):
            result = None
        else:
            result = self._output.pop(0)
        return result


class StorageHandler(object):
    """
    For classes that support internal storage (= dictionary).
    """

    @property
    def storage(self):
        """
        Returns the internal storage.

        :return: the internal storage
        :rtype: dict
        """
        raise Exception("Not implemented!")

    def expand(self, s):
        """
        Expands all occurrences of "@{...}" within the string with the actual values currently stored
        in internal storage.

        :param s: the string to expand
        :type s: str
        :return: the expanded string
        :rtype: str
        """
        result = s
        while result.find("@{") > -1:
            start = result.index("@{")
            end = result.index("}", start)
            name = result[start + 2:end]
            value = self.storage[name]
            if value is None:
                raise("Storage value '" + name + "' not present, failed to expand string: " + s)
            else:
                result = result[0:start] + str(value) + result[end + 1:]
        return result

    @classmethod
    def pad(cls, name):
        """
        Pads the name with "@{...}".

        :param name: the name to pad
        :type name: str
        :return: the padded name
        :rtype: str
        """
        if name.startswith("@{"):
            return name
        else:
            return "@{" + name + "}"

    @classmethod
    def extract(cls, padded):
        """
        Removes the surrounding "@{...}" from the name.

        :param padded: the padded string
        :type padded: str
        :return: the extracted name
        :rtype: str
        """
        if padded.startswith("@{") and padded.endswith("}"):
            return padded[2:len(padded)-1]
        else:
            return padded


def is_source(actor):
    """
    Checks whether the actor is a source.

    :param actor: the actor to check
    :type actor: Actor
    :return: True if the actor is a source
    :rtype: bool
    """
    return not isinstance(actor, InputConsumer) and isinstance(actor, OutputProducer)


def is_transformer(actor):
    """
    Checks whether the actor is a transformer.

    :param actor: the actor to check
    :type actor: Actor
    :return: True if the actor is a transformer
    :rtype: bool
    """
    return isinstance(actor, InputConsumer) and isinstance(actor, OutputProducer)


def is_sink(actor):
    """
    Checks whether the actor is a sink.

    :param actor: the actor to check
    :type actor: Actor
    :return: True if the actor is a sink
    :rtype: bool
    """
    return isinstance(actor, InputConsumer) and not isinstance(actor, OutputProducer)


def to_commandline(o):
    """
    Turns the object into a commandline string. However, first checks whether a string represents
    a internal value placeholder (@{...}).

    :param o: the object to turn into commandline
    :type o: object
    :return: the commandline
    :rtype: str
    """
    if isinstance(o, str) and o.startswith("@{") and o.endswith("}"):
        return o
    else:
        return classes.to_commandline(o)
