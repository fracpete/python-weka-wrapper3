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

# classes.py
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import os
import inspect
import argparse
import json
import logging
import re
import weka.core.typeconv as typeconv
import javabridge
from javabridge import JWrapper, JClassWrapper
from javabridge.jutil import JavaException
import weka.core.jvm as jvm

# logging setup
logger = logging.getLogger("weka.core.classes")


def get_class(classname):
    """
    Returns the class object associated with the dot-notation classname.

    Taken from here: http://stackoverflow.com/a/452981

    :param classname: the classname
    :type classname: str
    :return: the class object
    :rtype: object
    """
    parts = classname.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def get_jclass(classname):
    """
    Returns the Java class object associated with the dot-notation classname.

    :param classname: the classname
    :type classname: str
    :return: the class object
    :rtype: JB_Object
    """
    return javabridge.class_for_name(classname=classname)


def get_classname(obj):
    """
    Returns the classname of the JB_Object, Python class or object.

    :param obj: the java object or Python class/object to get the classname for
    :type obj: object
    :return: the classname
    :rtype: str
    """
    if isinstance(obj, javabridge.JB_Object):
        cls = javabridge.call(obj, "getClass", "()Ljava/lang/Class;")
        return javabridge.call(cls, "getName", "()Ljava/lang/String;")
    elif inspect.isclass(obj):
        return obj.__module__ + "." + obj.__name__
    else:
        return get_classname(obj.__class__)


class Stoppable(object):
    """
    Classes that can be stopped.
    """

    def is_stopped(self):
        """
        Returns whether the object has been stopped.

        :return: whether stopped
        :rtype: bool
        """
        raise Exception("Not implemented!")

    def stop_execution(self):
        """
        Triggers the stopping of the object.
        """
        raise Exception("Not implemented!")


from_dict_handlers = {}
"""
The methods that handle the restoration from a JSON dictionary, stored under their 'type'.
"""


def register_dict_handler(typestr, handler):
    """
    Registers a handler for restoring an object from a JSON dictionary.

    :param typestr: the type of the object
    :type typestr: str
    :param handler: the method
    """
    global from_dict_handlers
    from_dict_handlers[typestr] = handler


def deregister_dict_handler(typestr):
    """
    Deregisters a handler for restoring an object from a JSON dictionary.

    :param typestr: the type of the object
    :type typestr: str
    """
    global from_dict_handlers
    del from_dict_handlers[typestr]


def has_dict_handler(typestr):
    """
    Returns the handler for restoring an object from a JSON dictionary.

    :param typestr: the type of the object
    :type typestr: str
    :return: the handler, None if not available
    """
    global from_dict_handlers
    return typestr in from_dict_handlers


def get_dict_handler(typestr):
    """
    Returns the handler for restoring an object from a JSON dictionary.

    :param typestr: the type of the object
    :type typestr: str
    :return: the handler, None if not available
    """
    global from_dict_handlers
    return from_dict_handlers[str(typestr)]


class JSONObject(object):
    """
    Ancestor for classes that can be represented as JSON and restored from JSON.
    """

    def to_dict(self):
        """
        Returns a dictionary that represents this object, to be used for JSONification.

        :return: the object dictionary
        :rtype: dict
        """
        raise Exception("Not implemented!")

    @classmethod
    def from_dict(cls, d):
        """
        Restores an object state from a dictionary, used in de-JSONification.

        :param d: the object dictionary
        :type d: dict
        :return: the object
        :rtype: object
        """
        raise Exception("Not implemented!")

    def to_json(self):
        """
        Returns the options as JSON.

        :return: the object as string
        :rtype: str
        """
        return json.dumps(self.to_dict(), sort_keys=True, indent=2, separators=(',', ': '))

    @classmethod
    def from_json(cls, s):
        """
        Restores the object from the given JSON.

        :param s: the JSON string to parse
        :type s: str
        :return: the
        """
        d = json.loads(s)
        return get_dict_handler(d["type"])(d)

    def shallow_copy(self):
        """
        Returns a shallow copy of itself.

        :return: the copy
        :rtype: object
        """
        return self.from_json(self.to_json())


class Configurable(JSONObject):
    """
    The ancestor for all actors.
    """

    def __init__(self, config=None):
        """
        Initializes the object.

        :param config: the dictionary with the options (str -> object).
        :type config: dict
        """
        self._logger = None
        self._help = {}
        self._config = self.fix_config({})
        if config is not None:
            self.config = config
        if not has_dict_handler("Configurable"):
            register_dict_handler("Configurable", Configurable.from_dict)

    def __repr__(self):
        """
        Returns Python code for instantiating the object.

        :return: the representation
        :rtype: str
        """
        return \
            self.__class__.__module__ + "." + self.__class__.__name__ \
            + "(config=" + str(self.config) + ")"

    def description(self):
        """
        Returns a description of the object.

        :return: the description
        :rtype: str
        """
        raise Exception("Not implemented!")

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        return options

    @property
    def config(self):
        """
        Obtains the currently set options of the actor.

        :return: the options
        :rtype: dict
        """
        return self._config

    @config.setter
    def config(self, options):
        """
        Sets the options of the actor.

        :param options: the options
        :type options: dict
        """
        self._config = self.fix_config(options)

    def to_dict(self):
        """
        Returns a dictionary that represents this object, to be used for JSONification.

        :return: the object dictionary
        :rtype: dict
        """
        result = {}
        result["type"] = "Configurable"
        result["class"] = get_classname(self)
        result["config"] = {}
        for k in self._config:
            v = self._config[k]
            if isinstance(v, JSONObject):
                result["config"][k] = v.to_dict()
            else:
                result["config"][k] = v
        return result

    @classmethod
    def from_dict(cls, d):
        """
        Restores its state from a dictionary, used in de-JSONification.

        :param d: the object dictionary
        :type d: dict
        """
        conf = {}
        for k in d["config"]:
            v = d["config"][k]
            if isinstance(v, dict):
                conf[str(k)] = get_dict_handler(d["config"]["type"])(v)
            else:
                conf[str(k)] = v
        return get_class(str(d["class"]))(config=conf)

    def new_logger(self):
        """
        Returns a new logger instance.

        :return: the logger instance
        :rtype: logger
        """
        return logging.getLogger(get_classname(self))

    @property
    def logger(self):
        """
        Returns the logger object.

        :return: the logger
        :rtype: logger
        """
        if self._logger is None:
            self._logger = self.new_logger()
        return self._logger

    @property
    def help(self):
        """
        Obtains the help information per option for this actor.

        :return: the help
        :rtype: dict
        """
        return self._help

    def generate_help(self):
        """
        Generates a help string for this actor.

        :return: the help string
        :rtype: str
        """
        result = []
        result.append(self.__class__.__name__)
        result.append(re.sub(r'.', '=', self.__class__.__name__))
        result.append("")
        result.append("DESCRIPTION")
        result.append(self.description())
        result.append("")
        result.append("OPTIONS")
        opts = sorted(self.config.keys())
        for opt in opts:
            result.append(opt)
            helpstr = self.help[opt]
            if helpstr is None:
                helpstr = "-missing help-"
            result.append("\t" + helpstr)
            result.append("")
        return '\n'.join(result)

    def print_help(self):
        """
        Prints a help string for this actor to stdout.
        """
        print(self.generate_help())


class JavaObject(JSONObject):
    """
    Basic Java object.
    """
    
    def __init__(self, jobject):
        """
        Initializes the wrapper with the specified Java object.

        :param jobject: the Java object to wrap
        :type jobject: JB_Object
        """
        if jobject is None:
            raise Exception("No Java object supplied!")
        self.jobject = jobject
        if not has_dict_handler("JavaObject"):
            register_dict_handler("JavaObject", JavaObject.from_dict)

    def __str__(self):
        """
        Just calls the toString() method.

        :rtype: str
        """
        return javabridge.to_string(self.jobject)

    def __repr__(self):
        """
        Just calls the toString() method.

        :rtype: str
        """
        return javabridge.to_string(self.jobject)

    def __unicode__(self):
        """
        Just calls the toString() method.

        :rtype: str
        """
        return javabridge.to_string(self.jobject)

    @property
    def classname(self):
        """
        Returns the Java classname in dot-notation.

        :return: the Java classname
        :rtype: str
        """
        cls = javabridge.call(self.jobject, "getClass", "()Ljava/lang/Class;")
        return javabridge.call(cls, "getName", "()Ljava/lang/String;")

    def set_property(self, path, jobject):
        """
        Attempts to set the value (jobject, a Java object) of the provided (bean) property path.

        :param path: the property path, e.g., "filter" for a setFilter(...)/getFilter() method pair
        :type path: str
        :param jobject: the Java object to set; if instance of JavaObject class, the jobject member is automatically used
        :type jobject: JB_Object
        """
        # unwrap?
        if isinstance(jobject, JavaObject):
            jobject = jobject.jobject

        javabridge.static_call(
            "Lweka/core/PropertyPath;", "setValue",
            "(Ljava/lang/Object;Ljava/lang/String;Ljava/lang/Object;)V",
            self.jobject, path, jobject)

    def get_property(self, path):
        """
        Attempts to get the value (jobject, a Java object) of the provided (bean) property path.

        :param path: the property path, e.g., "filter" for a setFilter(...)/getFilter() method pair
        :type path: str
        :return: the wrapped Java object
        :rtype: JavaObject
        """
        return JavaObject(javabridge.static_call(
            "Lweka/core/PropertyPath;", "getValue",
            "(Ljava/lang/Object;Ljava/lang/String;)Ljava/lang/Object;",
            self.jobject, path))

    @property
    def jclass(self):
        """
        Returns the Java class object of the underlying Java object.

        :return: the Java class
        :rtype: JB_Object
        """
        return javabridge.call(self.jobject, "getClass", "()Ljava/lang/Class;")

    @property
    def jwrapper(self):
        """
        Returns a JWrapper instance of the encapsulated Java object, giving access to methods
        using dot notation.

        http://pythonhosted.org//javabridge/highlevel.html#wrapping-java-objects-using-reflection

        :return: the wrapper
        :rtype: JWrapper
        """
        return JWrapper(self.jobject)

    @property
    def jclasswrapper(self):
        """
        Returns a JClassWrapper instance of the class for the encapsulated Java object, giving
        access to the class methods using dot notation.

        http://pythonhosted.org//javabridge/highlevel.html#wrapping-java-objects-using-reflection

        :return: the wrapper
        :rtype: JClassWrapper
        """
        return JClassWrapper(javabridge.call(self.jobject, "getClass", "()Ljava/lang/Class;"))

    @property
    def is_serializable(self):
        """
        Returns true if the object is serialiable.

        :return: true if serializable
        :rtype: bool
        """
        return JavaObject.check_type(self.jobject, "java.io.Serializable")

    def to_dict(self):
        """
        Returns a dictionary that represents this object, to be used for JSONification.

        :return: the object dictionary
        :rtype: dict
        """
        result = {}
        result["type"] = "JavaObject"
        result["class"] = self.classname
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
        return JavaObject(cls.new_instance(d["class"]))

    @classmethod
    def check_type(cls, jobject, intf_or_class, jni_intf_or_class=None):
        """
        Returns whether the object implements the specified interface or is a subclass.
        E.g.: self._check_type('weka.core.OptionHandler', 'Lweka/core/OptionHandler;') 
        or self._check_type('weka.core.converters.AbstractFileLoader')

        :param jobject: the Java object to check
        :type jobject: JB_Object
        :param intf_or_class: the classname in Java notation (eg "weka.core.DenseInstance;")
        :type jni_intf_or_class: str
        :return: whether object implements interface or is subclass
        :rtype: bool
        """
        if jni_intf_or_class is None:
            jni_intf_or_class = "L" + intf_or_class.replace(".", "/") + ";"
        return javabridge.is_instance_of(jobject, jni_intf_or_class)
        
    @classmethod
    def enforce_type(cls, jobject, intf_or_class, jni_intf_or_class=None):
        """
        Raises an exception if the object does not implement the specified interface or is not a subclass. 
        E.g.: self._enforce_type('weka.core.OptionHandler', 'Lweka/core/OptionHandler;') 
        or self._enforce_type('weka.core.converters.AbstractFileLoader')

        :param jobject: the Java object to check
        :type jobject: JB_Object
        :param intf_or_class: the classname in Java notation (eg "weka.core.DenseInstance")
        :type intf_or_class: str
        :param jni_intf_or_class: the classname in JNI notation (eg "Lweka/core/DenseInstance;")
        :type jni_intf_or_class: str
        """
        if not cls.check_type(jobject, intf_or_class, jni_intf_or_class):
            raise TypeError("Object does not implement or subclass " + intf_or_class + ": " + get_classname(jobject))

    @classmethod
    def new_instance(cls, classname, jni_classname=None):
        """
        Creates a new object from the given classname using the default constructor, None in case of error.

        :param classname: the classname in Java notation (eg "weka.core.DenseInstance")
        :type classname: str
        :param jni_classname: the classname in JNI notation (eg "Lweka/core/DenseInstance;")
        :type jni_classname: str
        :return: the Java object
        :rtype: JB_Object
        """
        if jni_classname is None:
            jni_classname = classname.replace(".", "/")
        try:
            return javabridge.make_instance(jni_classname, "()V")
        except JavaException as e:
            print("Failed to instantiate " + classname + "/" + jni_classname + ": " + str(e))
            return None


class JavaArrayIterator(object):
    """
    Iterator for elements in a Java array.
    """
    def __init__(self, data):
        """
        :param data: the Java array to iterate over
        :type data: JavaArray
        """
        self.data = data
        self.index = 0
        self.length = len(data)

    def __iter__(self):
        """
        Returns itself.
        """
        return self

    def __next__(self):
        """
        Returns the next element from the array.

        :return: the next array element object, wrapped as JavaObject if not null
        :rtype: JavaObject or None
        """
        if self.index < self.length:
            index = self.index
            self.index += 1
            return self.data[index]
        else:
            raise StopIteration()


class JavaArray(JavaObject):
    """
    Convenience wrapper around Java arrays.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper with the specified Java object.

        :param jobject: the java array object to wrap
        :type jobject: JB_Object
        """
        super(JavaArray, self).__init__(jobject)
        c = self.jclass
        if not javabridge.call(c, "isArray", "()Z"):
            raise Exception("Not an array!")

    def __len__(self):
        """
        Returns the length of the array.

        :return: the array length
        :rtype: int
        """
        return javabridge.get_env().get_array_length(self.jobject)

    def __getitem__(self, key):
        """
        Returns the specified element in the array wrapped in a JavaObject.

        :param key: the index of the element to retrieve
        :type key: int
        :return: the element or None if element is null
        :rtype; JavaObject
        """
        if not isinstance(key, int):
            raise Exception("Key must be an integer!")
        element = javabridge.static_call(
            "Ljava/lang/reflect/Array;", "get", "(Ljava/lang/Object;I)Ljava/lang/Object;",
            self.jobject, key)
        if element is None:
            return None
        return JavaObject(element)

    def __setitem__(self, key, value):
        """
        Sets the specified element in the array.

        :param key: the index of the element to set
        :type key: int
        :param value: the object to set (JavaObject or JB_Object)
        """
        if isinstance(value, JavaObject):
            obj = value.jobject
        else:
            obj = value
        if not isinstance(key, int):
            raise Exception("Key must be an integer!")
        javabridge.static_call(
            "Ljava/lang/reflect/Array;", "set", "(Ljava/lang/Object;ILjava/lang/Object;)V",
            self.jobject, key, obj)

    def __delitem__(self, key):
        """
        Not implemented, raises an exception.
        """
        raise Exception("Cannot delete item from array!")

    def __iter__(self):
        """
        Returns an iterator over the elements.

        :return: the iterator
        :rtype: JavaArrayIterator
        """
        return JavaArrayIterator(self)

    @classmethod
    def new_instance(cls, classname, length):
        """
        Creates a new array with the given classname and length; initial values are null.

        :param classname: the classname in Java notation (eg "weka.core.DenseInstance")
        :type classname: str
        :param length: the length of the array
        :type length: int
        :return: the Java array
        :rtype: JB_Object
        """
        return javabridge.static_call(
            "Ljava/lang/reflect/Array;",
            "newInstance",
            "(Ljava/lang/Class;I)Ljava/lang/Object;",
            javabridge.class_for_name(classname=classname), length)


class Enum(JavaObject):
    """
    Wrapper for Java enums.
    """

    def __init__(self, jobject=None, enum=None, member=None):
        """
        Initializes the enum class.

        :param jobject: the Java object to wrap
        :type jobject: JB_Object
        :param enum: the enum class to instantiate (dot notation)
        :type enum: str
        :param member: the member of the enum class to instantiate
        :type member: str
        """
        if jobject is None:
            enumclass = javabridge.class_for_name(classname=enum)
            jobject = javabridge.static_call(
                "java/lang/Enum", "valueOf",
                "(Ljava/lang/Class;Ljava/lang/String;)Ljava/lang/Enum;",
                enumclass, member)
        super(Enum, self).__init__(jobject)

    @property
    def name(self):
        """
        Returns the name of the enum member.

        :return: the name
        :rtype: str
        """
        return javabridge.call(self.jobject, "name", "()Ljava/lang/String;")

    @property
    def ordinal(self):
        """
        Returns the ordinal of the enum member.

        :return: the ordinal
        :rtype: int
        """
        return javabridge.call(self.jobject, "ordinal", "()I")

    @property
    def values(self):
        """
        Returns list of all enum members.

        :return: all enum members
        :rtype: list
        """
        cls = javabridge.call(self.jobject, "getClass", "()Ljava/lang/Class;")
        clsname = javabridge.call(cls, "getName", "()Ljava/lang/String;")
        l = javabridge.static_call(clsname.replace(".", "/"), "values", "()[L" + clsname.replace(".", "/") + ";")
        l = javabridge.get_env().get_object_array_elements(l)
        result = []
        for item in l:
            result.append(Enum(jobject=item))
        return result


class Random(JavaObject):
    """
    Wrapper for the java.util.Random class.
    """

    def __init__(self, seed):
        """
        The seed value.

        :param seed: the seed value
        :type seed: int
        """
        super(Random, self).__init__(javabridge.make_instance("Ljava/util/Random;", "(J)V", seed))

    def next_int(self, n=None):
        """
        Next random integer. if n is provided, then between 0 and n-1.

        :param n: the upper limit (minus 1) for the random integer
        :type n: int
        :return: the next random integer
        :rtype: int
        """
        if n is None:
            return javabridge.call(self.jobject, "nextInt", "()I")
        else:
            return javabridge.call(self.jobject, "nextInt", "(I)I", n)

    def next_double(self):
        """
        Next random double.

        :return: the next random double
        :rtype: double
        """
        return javabridge.call(self.jobject, "nextDouble", "()D")


class Option(JavaObject):
    """
    Wrapper for the weka.core.Option class.
    """

    def __init__(self, jobject):
        """
        Initializes the wrapper with the specified option object.

        :param jobject: the java object to wrap
        :type jobject: JB_Object
        """
        super(Option, self).__init__(jobject)
        Option.enforce_type(jobject, "weka.core.Option")

    @property
    def name(self):
        """
        Returns the name of the option.

        :return: the name
        :rtype: str
        """
        return javabridge.call(self.jobject, "name", "()Ljava/lang/String;")

    @property
    def description(self):
        """
        Returns the description of the option.

        :return: the description
        :rtype: str
        """
        return javabridge.call(self.jobject, "description", "()Ljava/lang/String;")

    @property
    def synopsis(self):
        """
        Returns the synopsis of the option.

        :return: the synopsis
        :rtype: str
        """
        return javabridge.call(self.jobject, "synopsis", "()Ljava/lang/String;")

    @property
    def num_arguments(self):
        """
        Returns the synopsis of the option.

        :return: the synopsis
        :rtype: str
        """
        return javabridge.call(self.jobject, "numArguments", "()I")


class OptionHandler(JavaObject, Configurable):
    """
    Ancestor for option-handling classes. 
    Classes should implement the weka.core.OptionHandler interface to have any effect.
    """
    
    def __init__(self, jobject, options=None):
        """
        Initializes the wrapper with the specified Java object.

        :param jobject: the java object to wrap
        :type jobject: JB_Object
        :param options: the options to set
        :type options: list
        """
        super(OptionHandler, self).__init__(jobject)
        self.is_optionhandler = OptionHandler.check_type(jobject, "weka.core.OptionHandler")
        if (options is not None) and (len(options) > 0):
            self.options = options
        # we have to manually instantiate some objects, since multiple inheritance doesn't call
        # Configurable constructor
        self._logger = None
        self._help = {}
        self._config = self.fix_config({})
        if not has_dict_handler("OptionHandler"):
            register_dict_handler("OptionHandler", OptionHandler.from_dict)

    def global_info(self):
        """
        Returns the globalInfo() result, None if not available.

        :rtypes: str
        """
        try:
            return javabridge.call(self.jobject, "globalInfo", "()Ljava/lang/String;")
        except JavaException:
            return None

    def description(self):
        """
        Returns a description of the object.

        :return: the description
        :rtype: str
        """
        return self.global_info()

    @property
    def options(self):
        """
        Obtains the currently set options as list.

        :return: the list of options
        :rtype: list
        """
        if self.is_optionhandler:
            return typeconv.string_array_to_list(javabridge.call(self.jobject, "getOptions", "()[Ljava/lang/String;"))
        else:
            return []

    @options.setter
    def options(self, options):
        """
        Sets the command-line options (as list).

        :param options: the list of command-line options to set
        :type options: list
        """
        if self.is_optionhandler:
            javabridge.call(self.jobject, "setOptions", "([Ljava/lang/String;)V", typeconv.string_list_to_array(options))

    def to_commandline(self):
        """
        Generates a commandline string from the JavaObject instance.

        :return: the commandline string
        :rtype: str
        """
        return javabridge.static_call(
            "Lweka/core/Utils;", "toCommandLine",
            "(Ljava/lang/Object;)Ljava/lang/String;",
            self.jobject)

    def to_help(self):
        """
        Returns a string that contains the 'global_info' text and the options.

        :return: the generated help string
        :rtype: str
        """
        result = []
        result.append(self.classname)
        result.append("=" * len(self.classname))
        result.append("")
        result.append("DESCRIPTION")
        result.append("")
        result.append(self.global_info())
        result.append("")
        result.append("OPTIONS")
        result.append("")
        options = javabridge.call(self.jobject, "listOptions", "()Ljava/util/Enumeration;")
        enum = javabridge.get_enumeration_wrapper(options)
        while enum.hasMoreElements():
            opt = Option(enum.nextElement())
            result.append(opt.synopsis)
            result.append(opt.description)
            result.append("")
        return '\n'.join(result)

    def __str__(self):
        """
        Calls the toString() method of the java object.

        :return: the result of the toString() method
        :rtype: str
        """
        return javabridge.to_string(self.jobject)

    def to_dict(self):
        """
        Returns a dictionary that represents this object, to be used for JSONification.

        :return: the object dictionary
        :rtype: dict
        """
        result = super(OptionHandler, self).to_dict()
        result["type"] = "OptionHandler"
        result["options"] = join_options(self.options)
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
        result = OptionHandler(cls.new_instance(d["class"]))
        result.options = split_options(d["options"])
        return result


class SingleIndex(JavaObject):
    """
    Wrapper for a Weka SingleIndex object.
    """

    def __init__(self, jobject=None, index=None):
        """
        Initializes the wrapper with the specified Java object or string index.

        :param jobject: the java object to wrap
        :type jobject: JB_Object
        :param index: the string index to use
        :type index: str
        """
        if jobject is None:
            if index is None:
                jobject = javabridge.make_instance("weka/core/SingleIndex", "()V")
            else:
                jobject = javabridge.make_instance("weka/core/SingleIndex", "(Ljava/lang/String;)V", index)
        else:
            self.enforce_type(jobject, "weka.core.SingleIndex")
        super(SingleIndex, self).__init__(jobject)

    def upper(self, upper):
        """
        Sets the upper limit.

        :param upper: the upper limit
        :type upper: int
        """
        javabridge.call(self.jobject, "setUpper", "(I)V", upper)

    def index(self):
        """
        Returns the integer index.

        :return: the 0-based integer index
        :rtype: int
        """
        return javabridge.call(self.jobject, "getIndex", "()I")

    @property
    def single_index(self):
        """
        Returns the string index.

        :return: the 1-based string index
        :rtype: str
        """
        return javabridge.call(self.jobject, "getSingleIndex", "()Ljava/lang/String;")

    @single_index.setter
    def single_index(self, index):
        """
        Sets the string index.

        :param index: the 1-based string index
        ::type index: str
        """
        javabridge.call(self.jobject, "setSingleIndex", "(Ljava/lang/String;)V", index)


class Range(JavaObject):
    """
    Wrapper for a Weka Range object.
    """

    def __init__(self, jobject=None, ranges=None):
        """
        Initializes the wrapper with the specified Java object or string range.

        :param jobject: the java object to wrap
        :type jobject: JB_Object
        :param ranges: the string range to use
        :type ranges: str
        """
        if jobject is None:
            if ranges is None:
                jobject = javabridge.make_instance("weka/core/Range", "()V")
            else:
                jobject = javabridge.make_instance("weka/core/Range", "(Ljava/lang/String;)V", ranges)
        else:
            self.enforce_type(jobject, "weka.core.Range")
        super(Range, self).__init__(jobject)

    def upper(self, upper):
        """
        Sets the upper limit.

        :param upper: the upper limit
        :type upper: int
        """
        javabridge.call(self.jobject, "setUpper", "(I)V", upper)

    def selection(self):
        """
        Returns the selection list.

        :return: the list of 0-based integer indices
        :rtype: list
        """
        return javabridge.get_env().get_int_array_elements(javabridge.call(self.jobject, "getSelection", "()[I"))

    @property
    def ranges(self):
        """
        Returns the string range.

        :return: the string range of 1-based indices
        :rtype: str
        """
        return javabridge.call(self.jobject, "getRanges", "()Ljava/lang/String;")

    @ranges.setter
    def ranges(self, rng):
        """
        Sets the string range.

        :param rng: the range to set
        :type rng: str
        """
        javabridge.call(self.jobject, "setRanges", "(Ljava/lang/String;)V", rng)

    @property
    def invert(self):
        """
        Returns whether the range is inverted.

        :return: true if inverted
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getInvert", "()Z")

    @invert.setter
    def invert(self, invert):
        """
        Sets the invert state.

        :param invert: whether to invert or not
        :type invert: bool
        """
        javabridge.call(self.jobject, "setInvert", "(Z)V", invert)


class Tag(JavaObject):
    """
    Wrapper for the weka.core.Tag class.
    """

    def __init__(self, jobject=None, ident=None, ident_str="", readable="", uppercase=True):
        """
        :param jobject: the java object to wrap
        :type jobject: JB_Object
        :param ident: the ID integer associated with the tag
        :type ident: int
        :param ident_str: the ID string associated with the tag (case-insensitive)
        :type ident_str: str
        :param readable: the text of the tag
        :type readable: str
        :param uppercase: whether to uppercase the id string
        :type uppercase: bool
        """
        if jobject is None:
            jobject = javabridge.make_instance(
                "weka/core/Tag", "(ILjava/lang/String;Ljava/lang/String;Z)V",
                ident, ident_str, readable, uppercase)
        else:
            self.enforce_type(jobject, "weka.core.Tag")
        super(Tag, self).__init__(jobject)

    @property
    def ident(self):
        """
        Returns the current integer ID of the tag.

        :return: the integer ID
        :rtype: int
        """
        return javabridge.call(self.jobject, "getID", "()I")

    @ident.setter
    def ident(self, value):
        """
        Sets the integer ID of the tag.

        :param value: the new ID
        :type value: int
        """
        javabridge.call(self.jobject, "setID", "(I)V", value)

    @property
    def identstr(self):
        """
        Returns the current ID string.

        :return: the ID string
        :rtype: str
        """
        return javabridge.call(self.jobject, "getIDStr", "()Ljava/lang/String;")

    @identstr.setter
    def identstr(self, value):
        """
        Sets the ID string.

        :param value: the new ID string
        :type value: str
        """
        javabridge.call(self.jobject, "setIDStr", "(Ljava/lang/String;)V", value)

    @property
    def readable(self):
        """
        Returns the 'human readable' string.

        :return: the readable string
        :rtype: str
        """
        return javabridge.call(self.jobject, "getReadable", "()Ljava/lang/String;")

    @readable.setter
    def readable(self, value):
        """
        Sets the 'human readable' string.

        :param value: the new readable string
        :type value: str
        """
        javabridge.call(self.jobject, "setReadable", "(Ljava/lang/String;)V", value)


class Tags(JavaObject):
    """
    Wrapper for an array of weka.core.Tag objects.
    """

    def __init__(self, jobject=None, tags=None):
        """
        :param jobject: the Java Tag array to wrap.
        :type jobject: JB_Object
        :param tags: the list of Tag objects to use
        :type tags: list
        """
        if tags is not None:
            jarray = JavaArray(JavaArray.new_instance("weka.core.Tag", len(tags)))
            for i in range(len(tags)):
                jarray[i] = tags[i]
            jobject = jarray.jobject
        self.enforce_type(jobject, "weka.core.Tag", jni_intf_or_class="[Lweka/core/Tag;")
        super(Tags, self).__init__(jobject)
        self.array = JavaArray(self.jobject)

    def __len__(self):
        """
        Returns the number of Tag objects in the array.

        :return: the number of tag objects
        :rtype: int
        """
        return len(self.array)

    def __getitem__(self, item):
        """
        Returns the specified Tag from the array.

        :param item: the 0-based index
        :type item: int
        :return: the tag
        :rtype: Tag
        """
        return Tag(self.array[item].jobject)

    def __setitem__(self, key, value):
        """
        Not implemented.
        """
        raise Exception("Cannot set a Tag!")

    def __delitem__(self, key):
        """
        Not implemented.
        """
        raise Exception("Cannot delete a Tag!")

    def __str__(self):
        """
        Just calls the toString() method.

        :rtype: str
        """
        result = ""
        for i in range(len(self.array)):
            if i > 0:
                result += "|"
            result += str(self.array[i])
        return result

    def find(self, name):
        """
        Returns the Tag that matches the name.

        :param name: the string representation of the tag
        :type name: str
        :return: the tag, None if not found
        :rtype: Tag
        """
        result = None
        for t in self.array:
            if str(t) == name:
                result = Tag(t.jobject)
                break
        return result

    @classmethod
    def get_tags(cls, classname, field):
        """
        Instantiates the Tag array located in the specified class with the given field name.

        Example:
        tags = Tags.get_tags("weka.classifiers.functions.SMO", "TAGS_FILTER")

        :param classname: the classname in which the tags reside
        :type classname: str
        :param field: the field name of the Tag array
        :type field: str
        :return: the Tags objects
        :rtype: Tags
        """
        classname = "L" + classname.replace(".", "/") + ";"
        return Tags(jobject=javabridge.get_static_field(classname, field, "[Lweka/core/Tag;"))

    @classmethod
    def get_object_tags(cls, javaobject, methodname):
        """
        Instantiates the Tag array obtained from the object using the specified method name.

        Example:
        cls = Classifier(classname="weka.classifiers.meta.MultiSearch")
        tags = Tags.get_object_tags(cls, "getMetricsTags")

        :param javaobject: the javaobject to obtain the tags from
        :type javaobject: JavaObject
        :param methodname: the method name returning the Tag array
        :type methodname: str
        :return: the Tags objects
        :rtype: Tags
        """
        return Tags(jobject=javabridge.call(javaobject.jobject, methodname, "()[Lweka/core/Tag;"))


class SelectedTag(JavaObject):
    """
    Wrapper for the weka.core.SelectedTag class.
    """

    def __init__(self, jobject=None, tag_id=None, tag_text=None, tags=None):
        """
        Initializes the wrapper with the specified Java object or tags and either tag_id or tag_text.

        :param jobject: the java object to wrap
        :type jobject: JB_Object
        :param tag_id: the integer associated with the tag
        :type tag_id: int
        :param tag_text: the text associated with the tag
        :type tag_text: str
        :param tags: list of Tag objects or Tags wrapper object
        :type tags: list or Tags
        """

        if isinstance(tags, Tags):
            tobj = tags.jobject
        else:
            tobj = tags

        if jobject is None:
            if tag_id is None:
                jobject = javabridge.make_instance(
                    "weka/core/SelectedTag", "(Ljava/lang/String;[Lweka/core/Tag;)V", tag_text, tobj)
            else:
                jobject = javabridge.make_instance(
                    "weka/core/SelectedTag", "(I[Lweka/core/Tag;)V", tag_id, tobj)
        else:
            self.enforce_type(jobject, "weka.core.SelectedTag")
        super(SelectedTag, self).__init__(jobject)

    @property
    def selected(self):
        """
        Returns the selected tag.

        :return: the tag
        :rtype: Tag
        """
        return Tag(javabridge.call(self.jobject, "getSelectedTag", "()Lweka/core/Tag;"))

    @property
    def tags(self):
        """
        Returns the associated tags.

        :return: the list of Tag objects
        :rtype: list
        """
        result = []
        a = javabridge.call(self.jobject, "getTags", "()Lweka/core/Tag;]")
        length = javabridge.get_env().get_array_length(a)
        wrapped = javabridge.get_env().get_object_array_elements(a)
        for i in range(length):
            result.append(Tag(javabridge.get_env().get_string(wrapped[i])))
        return result


def join_options(options):
    """
    Turns the list of options back into a single commandline string.

    :param options: the list of options to process
    :type options: list
    :return: the combined options
    :rtype: str
    """
    return javabridge.static_call(
        "Lweka/core/Utils;", "joinOptions",
        "([Ljava/lang/String;)Ljava/lang/String;",
        options)


def split_options(cmdline):
    """
    Splits the commandline into a list of options.

    :param cmdline: the commandline string to split into individual options
    :type cmdline: str
    :return: the split list of commandline options
    :rtype: list
    """
    return typeconv.string_array_to_list(
        javabridge.static_call(
            "Lweka/core/Utils;", "splitOptions",
            "(Ljava/lang/String;)[Ljava/lang/String;",
            cmdline))


def backquote(s):
    """
    Backquotes the string.

    :param s: the string to process
    :type s: str
    :return: the backquoted string
    :rtype: str
    """
    return javabridge.static_call(
        "Lweka/core/Utils;", "backQuoteChars", "(Ljava/lang/String;)Ljava/lang/String;", s)


def unbackquote(s):
    """
    Un-backquotes the string.

    :param s: the string to process
    :type s: str
    :return: the un-backquoted string
    :rtype: str
    """
    return javabridge.static_call(
        "Lweka/core/Utils;", "unbackQuoteChars", "(Ljava/lang/String;)Ljava/lang/String;", s)


def quote(s):
    """
    Quotes the string if necessary.

    :param s: the string to process
    :type s: str
    :return: the quoted string
    :rtype: str
    """
    return javabridge.static_call(
        "Lweka/core/Utils;", "quote", "(Ljava/lang/String;)Ljava/lang/String;", s)


def unquote(s):
    """
    Un-quotes the string.

    :param s: the string to process
    :type s: str
    :return: the un-quoted string
    :rtype: str
    """
    return javabridge.static_call(
        "Lweka/core/Utils;", "unquote", "(Ljava/lang/String;)Ljava/lang/String;", s)


def to_commandline(optionhandler):
    """
    Generates a commandline string from the OptionHandler instance.

    :param optionhandler: the OptionHandler instance to turn into a commandline
    :type optionhandler: OptionHandler
    :return: the commandline string
    :rtype: str
    """
    return javabridge.static_call(
        "Lweka/core/Utils;", "toCommandLine",
        "(Ljava/lang/Object;)Ljava/lang/String;",
        optionhandler.jobject)


def from_commandline(cmdline, classname=None):
    """
    Creates an OptionHandler based on the provided commandline string.

    :param cmdline: the commandline string to use
    :type cmdline: str
    :param classname: the classname of the wrapper to return other than OptionHandler (in dot-notation)
    :type classname: str
    :return: the generated option handler instance
    :rtype: object
    """
    params = split_options(cmdline)
    cls = params[0]
    params = params[1:]
    handler = OptionHandler(jobject=javabridge.make_instance(cls.replace(".", "/"), "()V"), options=params)
    if classname is None:
        return handler
    else:
        c = get_class(classname)
        return c(jobject=handler.jobject)


class AbstractParameter(OptionHandler):
    """
    Ancestor for all parameter classes used by SetupGenerator and MultiSearch.
    """

    def __init__(self, classname=None, jobject=None, options=None):
        """
        Initializes the specified parameter using either the classname or the supplied JB_Object.

        :param classname: the classname of the search parameter
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = AbstractParameter.new_instance(classname)
        self.enforce_type(jobject, "weka.core.setupgenerator.AbstractParameter")
        super(AbstractParameter, self).__init__(jobject=jobject, options=options)

    @property
    def prop(self):
        """
        Returns the currently set property to apply the parameter to.

        :return: the property
        :rtype: str
        """
        return javabridge.call(self.jobject, "getProperty", "()Ljava/lang/String;")

    @prop.setter
    def prop(self, s):
        """
        Sets the property to apply the parameter to.

        :param s: the property
        :type s: str
        """
        javabridge.call(self.jobject, "setProperty", "(Ljava/lang/String;)V", s)


class ListParameter(AbstractParameter):
    """
    Parameter using a predefined list of values, used by SetupGenerator and MultiSearch.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified parameter using either its classname or the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        classname = "weka.core.setupgenerator.ListParameter"
        if jobject is None:
            jobject = ListParameter.new_instance(classname)
        self.enforce_type(jobject, "weka.core.setupgenerator.ListParameter")
        super(ListParameter, self).__init__(jobject=jobject, options=options)

    @property
    def values(self):
        """
        Returns the currently set values.

        :return: the list of values (strings)
        :rtype: list
        """
        return split_options(javabridge.call(self.jobject, "getList", "()Ljava/lang/String;"))

    @values.setter
    def values(self, l):
        """
        Sets the list of values to apply.

        :param l: the list of values (strings)
        :type l: list
        """
        javabridge.call(self.jobject, "setList", "(Ljava/lang/String;)V", join_options(l))


class MathParameter(AbstractParameter):
    """
    Parameter using a math expression for generating values, used by SetupGenerator and MultiSearch.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified parameter using either its classname or the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        classname = "weka.core.setupgenerator.MathParameter"
        if jobject is None:
            jobject = ListParameter.new_instance(classname)
        self.enforce_type(jobject, "weka.core.setupgenerator.MathParameter")
        super(MathParameter, self).__init__(jobject=jobject, options=options)

    @property
    def minimum(self):
        """
        Returns the currently set minimum value.

        :return: the minimum
        :rtype: float
        """
        return javabridge.call(self.jobject, "getMin", "()D")

    @minimum.setter
    def minimum(self, m):
        """
        Sets the new minimum value.

        :param m: the minimum
        :type m: float
        """
        javabridge.call(self.jobject, "setMin", "(D)V", m)

    @property
    def maximum(self):
        """
        Returns the currently set maximum value.

        :return: the maximum
        :rtype: float
        """
        return javabridge.call(self.jobject, "getMax", "()D")

    @maximum.setter
    def maximum(self, m):
        """
        Sets the new maximum value.

        :param m: the maximum
        :type m: float
        """
        javabridge.call(self.jobject, "setMax", "(D)V", m)

    @property
    def step(self):
        """
        Returns the currently set step value.

        :return: the step
        :rtype: float
        """
        return javabridge.call(self.jobject, "getStep", "()D")

    @step.setter
    def step(self, s):
        """
        Sets the new step value.

        :param s: the step
        :type s: float
        """
        javabridge.call(self.jobject, "setStep", "(D)V", s)

    @property
    def base(self):
        """
        Returns the currently set base value.

        :return: the base
        :rtype: float
        """
        return javabridge.call(self.jobject, "getBase", "()D")

    @base.setter
    def base(self, b):
        """
        Sets the new base value.

        :param b: the base
        :type b: float
        """
        javabridge.call(self.jobject, "setBase", "(D)V", b)

    @property
    def expression(self):
        """
        Returns the currently set expression.

        :return: the expression
        :rtype: str
        """
        return javabridge.call(self.jobject, "getExpression", "()Ljava/lang/String;")

    @expression.setter
    def expression(self, e):
        """
        Sets the new expression.

        :param e: the expression
        :type e: str
        """
        javabridge.call(self.jobject, "setExpression", "(Ljava/lang/String;)V", e)


class SetupGenerator(OptionHandler):
    """
    Allows generation of large number of setups using parameter setups.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified classifier using its classname or the supplied JB_Object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        classname = "weka.core.SetupGenerator"
        if jobject is None:
            jobject = OptionHandler.new_instance(classname)
        else:
            self.enforce_type(jobject, classname)
        super(SetupGenerator, self).__init__(jobject=jobject, options=options)

    @property
    def base_object(self):
        """
        Returns the base object to apply the setups to.

        :return: the base object
        :rtype: JavaObject or OptionHandler
        """
        jobj = javabridge.call(self.jobject, "getBaseObject", "()Ljava/io/Serializable;")
        if OptionHandler.check_type(jobj, "weka.core.OptionHandler"):
            return OptionHandler(jobj)
        else:
            return JavaObject(jobj)

    @base_object.setter
    def base_object(self, obj):
        """
        Sets the base object to apply the setups to.

        :param obj: the object to use (must be serializable!)
        :type obj: JavaObject
        """
        if not obj.is_serializable:
            raise Exception("Base object must be serializable: " + obj.classname)
        javabridge.call(self.jobject, "setBaseObject", "(Ljava/io/Serializable;)V", obj.jobject)

    @property
    def parameters(self):
        """
        Returns the list of currently set search parameters.

        :return: the list of AbstractSearchParameter objects
        :rtype: list
        """
        array = JavaArray(javabridge.call(self.jobject, "getParameters", "()[Lweka/core/setupgenerator/AbstractParameter;"))
        result = []
        for item in array:
            result.append(AbstractParameter(jobject=item.jobject))
        return result

    @parameters.setter
    def parameters(self, params):
        """
        Sets the list of search parameters to use.

        :param params: list of AbstractSearchParameter objects
        :type params: list
        """
        array = JavaArray(jobject=JavaArray.new_instance("weka.core.setupgenerator.AbstractParameter", len(params)))
        for idx, obj in enumerate(params):
            array[idx] = obj.jobject
        javabridge.call(self.jobject, "setParameters", "([Lweka/core/setupgenerator/AbstractParameter;)V", array.jobject)

    def setups(self):
        """
        Generates and returns all the setups according to the parameter search space.

        :return: the list of configured objects (of type JavaObject)
        :rtype: list
        """
        result = []
        has_options = self.base_object.is_optionhandler
        enm = javabridge.get_enumeration_wrapper(javabridge.call(self.jobject, "setups", "()Ljava/util/Enumeration;"))
        while enm.hasMoreElements():
            if has_options:
                result.append(OptionHandler(enm.nextElement()))
            else:
                result.append(JavaObject(enm.nextElement()))
        return result


def main():
    """
    Runs a classifier from the command-line. Calls JVM start/stop automatically.
    Use -h to see all options.
    """
    parser = argparse.ArgumentParser(
        description='Performs option handling operations from the command-line. Calls JVM start/stop automatically.')
    parser.add_argument("-j", metavar="classpath", dest="classpath", help="additional classpath, jars/directories")
    parser.add_argument("-action", metavar="action", dest="action", required=True,
                        help="The action to perform on the options: join=create single string, "\
                             "split=create array from quoted option, code=generate code from options")
    parser.add_argument("option", nargs=argparse.REMAINDER, help="The option(s) to process")
    parsed = parser.parse_args()
    jars = []
    if parsed.classpath is not None:
        jars = parsed.classpath.split(os.pathsep)

    jvm.start(jars, packages=True)

    try:
        if parsed.action == "join":
            output = "cmdline = \"" + backquote(join_options(parsed.option)) + "\""
        elif parsed.action == "split" and len(parsed.option) == 1:
            output = "options = [\n"
            opts = split_options(parsed.option[0])
            for idx, opt in enumerate(opts):
                if idx > 0:
                    output += ",\n"
                output += "    \"" + backquote(opt) + "\""
            output += "]"
        elif parsed.action == "code":
            options = parsed.option[:]
            cname = None
            # classname + options?
            if options[0].find(".") > -1:
                cname = options[0]
                options = options[1:]
            output = "options = [ \n"
            for idx, opt in enumerate(options):
                if idx > 0:
                    output += ",\n"
                output += "    \"" + backquote(opt) + "\""
            output += "]\n"
            if cname is not None:
                output += 'handler = OptionHandler(JavaObject.new_instance("' + cname + '"))\n'
                output += 'handler.options = options\n'
        else:
            raise Exception("Unsupported action: " + parsed.action)
        if output is not None:
            print(output)
    except Exception as e:
        print(e)
    finally:
        jvm.stop()

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
