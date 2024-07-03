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
# Copyright (C) 2014-2024 Fracpete (pythonwekawrapper at gmail dot com)

import os
import inspect
import argparse
import logging
import csv
import sys
import traceback

import numpy

import weka.core.typeconv as typeconv
from jpype import JClass, JObject, JException, JArray
from confobj import Configurable, JSONObject, has_dict_handler, register_dict_handler, get_class
import weka.core.jvm as jvm

# logging setup
logger = logging.getLogger("weka.core.classes")

suggestions = None
""" dictionary for class -> package relation """


def deepcopy(obj):
    """
    Creates a deep copy of the JavaObject (or derived class) or JB_Object.

    :param obj: the object to create a copy of
    :type obj: object
    :return: the copy, None if failed to copy
    :rtype: object
    """
    if isinstance(obj, JavaObject):
        wrapped = True
        jobject = obj.jobject
    else:
        wrapped = False
        jobject = obj
    try:
        serialized = JClass("weka.core.SerializedObject")(jobject)
        jcopy = serialized.getObject()
        if wrapped:
            jcopy = obj.__class__(jobject=jcopy)
        return jcopy
    except JException as e:
        print("Failed to create copy of " + get_classname(obj) + ": " + str(e))
        return None


def serialization_read(filename):
    """
    Reads the serialized object from disk. Caller must wrap object in appropriate Python wrapper class.

    :param filename: the file with the serialized object
    :type filename: str
    :return: the JB_Object
    :rtype: JB_Object
    """
    return JClass("weka.core.SerializationHelper").read(filename)


def serialization_read_all(filename):
    """
    Reads the serialized objects from disk. Caller must wrap objects in appropriate Python wrapper classes.

    :param filename: the file with the serialized objects
    :type filename: str
    :return: the list of JB_OBjects
    :rtype: list
    """
    array = JClass("weka.core.SerializationHelper").readAll(filename)
    if array is None:
        return None
    else:
        return typeconv.from_jobject_array(array)


def serialization_write(filename, jobject):
    """
    Serializes the object to disk. JavaObject instances get automatically unwrapped.

    :param filename: the file to serialize the object to
    :type filename: str
    :param jobject: the object to serialize
    :type jobject: JB_Object or JavaObject
    """
    if isinstance(jobject, JavaObject):
        jobject = jobject.jobject
    JClass("weka.core.SerializationHelper").write(filename, jobject)


def serialization_write_all(filename, jobjects):
    """
    Serializes the list of objects to disk. JavaObject instances get automatically unwrapped.

    :param filename: the file to serialize the object to
    :type filename: str
    :param jobjects: the list of objects to serialize
    :type jobjects: list
    """
    array = JObject[len(jobjects)]
    for i in range(len(jobjects)):
        obj = jobjects[i]
        if isinstance(obj, JavaObject):
            obj = obj.jobject
        array[i] = obj
    JClass("weka.core.SerializationHelper").writeAll(filename, array)


def to_byte_array(jobjects):
    """
    Serializes the list of objects into a numpy array.

    :param jobjects: the list of objects to serialize
    :type jobjects: list
    :return: the numpy array
    :rtype: ndarray
    """
    array = new_array("java.lang.Object", len(jobjects))
    for i in range(len(jobjects)):
        obj = jobjects[i]
        if isinstance(obj, JavaObject):
            obj = obj.jobject
        array[i] = obj
    byte_array = JClass("weka.core.PickleHelper").toByteArray(array)
    return numpy.asarray(byte_array)


def from_byte_array(array):
    """
    Deserializes Java objects from the numpy array.

    :param array: the numpy array to deserialize the Java objects from
    :type array: ndarray
    :return: the list of deserialized JB_Object instances
    :rtype: list
    """
    obj_array = JClass("weka.core.PickleHelper").fromByteArray(JArray.of(array))
    return typeconv.from_jobject_array(obj_array)


def get_jclass(classname):
    """
    Returns the Java class object associated with the dot-notation classname.
    Also supports the Java primitives: boolean, byte, short, int, long, float, double, char.

    :param classname: the classname
    :type classname: str
    :return: the class object
    :rtype: JB_Object
    """
    # primitive?
    if "." not in classname:
        if classname == "boolean":
            return get_static_field("java.lang.Boolean", "TYPE")
        elif classname == "byte":
            return get_static_field("java.lang.Byte", "TYPE")
        elif classname == "short":
            return get_static_field("java.lang.Short", "TYPE")
        elif classname == "int":
            return get_static_field("java.lang.Integer", "TYPE")
        elif classname == "long":
            return get_static_field("java.lang.Long", "TYPE")
        elif classname == "float":
            return get_static_field("java.lang.Float", "TYPE")
        elif classname == "double":
            return get_static_field("java.lang.Double", "TYPE")
        elif classname == "char":
            return get_static_field("java.lang.Character", "TYPE")

    if jvm.with_package_support:
        try:
            return JClass("weka.core.ClassHelper").forName(JClass("java.lang.Object"), classname)
        except:
            return JClass("weka.core.ClassHelper").newInstance(classname, None, None)
    else:
        return JClass(classname)


def get_enum(classname, enm):
    """
    Returns the instance of the enum.

    :param classname: the classname of the enum
    :type classname: str
    :param enm: the name of the enum element to return
    :type enm: str
    :return: the enum instance
    :rtype: JB_Object
    """
    return JClass("weka.core.ClassHelper").getEnum(classname, enm)


def get_static_field(classname, fieldname):
    """
    Returns the Java object associated with the static field of the specified class.

    :param classname: the classname of the class to get the field from
    :type classname: str
    :param fieldname: the name of the field to retriev
    :type fieldname: str
    :return: the object
    :rtype: JB_Object
    """
    if jvm.with_package_support:
        return JClass("weka.core.ClassHelper").getStaticField(classname, fieldname)
    else:
        return getattr(JClass(classname), fieldname)


def get_classname(obj):
    """
    Returns the classname of the JB_Object, Python class or object.

    :param obj: the java object or Python class/object to get the classname for
    :type obj: object
    :return: the classname
    :rtype: str
    """
    if isinstance(obj, JObject):
        return obj.getClass().getName()
    elif inspect.isclass(obj):
        return obj.__module__ + "." + obj.__name__
    else:
        return get_classname(obj.__class__)


def is_instance_of(obj, class_or_intf_name):
    """
    Checks whether the Java object implements the specified interface or is a subclass of the superclass.

    :param obj: the Java object to check
    :type obj: JB_Object
    :param class_or_intf_name: the superclass or interface to check, dot notation or with forward slashes
    :type class_or_intf_name: str
    :return: true if either implements interface or subclass of superclass
    :rtype: bool
    """
    class_or_intf_name = class_or_intf_name.replace("/", ".")
    classname = get_classname(obj)
    # array? retrieve component type and check that
    if is_array(obj):
        jarray = JavaArray(jobject=obj)
        classname = jarray.component_type()
    InheritanceUtils = JClass("weka.core.InheritanceUtils")
    result = InheritanceUtils.isSubclass(class_or_intf_name, classname)
    if result:
        return True
    return InheritanceUtils.hasInterface(class_or_intf_name, classname)


def is_array(obj):
    """
    Checks whether the Java object is an array.

    :param obj: the Java object to check
    :type obj: JB_Object
    :return: whether the object is an array
    :rtype: bool
    """
    return obj.getClass().isArray()


def list_property_names(obj):
    """
    Lists the property names (Bean properties, ie read/write method pair) of the Java object.

    :param obj: the object to inspect
    :type obj: JB_Object or JavaObject
    :return: the list of property names
    :rtype: list
    """
    if isinstance(obj, JavaObject):
        obj = obj.jobject

    return typeconv.jstring_array_to_list(JClass("weka.core.ClassHelper").listPropertyNames(obj))


def new_instance(classname):
    """
    Instantiates an object of the specified class. Does not raise an Exception
    if it fails to do so (opposed to JavaObject.new_array).

    :param classname: the name of the class to instantiate
    :type classname: str
    :return: the object, None if failed to instantiate
    :rtype: JB_Object
    """
    return JClass("weka.core.ClassHelper").newInstance(classname, None, None)


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
        self._make_calls()
        self._property_path = None

    def __str__(self):
        """
        Just calls the toString() method.

        :rtype: str
        """
        return str(self.jobject)

    def __repr__(self):
        """
        Just calls the toString() method.

        :rtype: str
        """
        return str(self.jobject)

    def __unicode__(self):
        """
        Just calls the toString() method.

        :rtype: str
        """
        return str(self.jobject)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove JB_Object and replace with serialized byte array (ie numpy array)
        del state["jobject"]
        # Remove objects generated by javabridge.make_call
        make_calls = []
        for k in state.keys():
            if k.startswith("_mc_"):
                make_calls.append(k)
        for k in make_calls:
            del state[k]
        # serialize jobject
        state["jobject_bytes"] = None
        if self.jobject is not None:
            try:
                state["jobject_bytes"] = to_byte_array([self.jobject])
            except:
                traceback.print_exc()
                raise Exception("Java object is not serializable: " + get_classname(self.jobject))
        return state

    def __setstate__(self, state):
        # Restore JB_Object instance from byte array.
        self.__dict__.update(state)
        self.jobject = None
        if hasattr(self, "jobject_bytes") and (self.jobject_bytes is not None):
            try:
                jobjects = from_byte_array(self.jobject_bytes)
                if len(jobjects) > 0:
                    self.jobject = jobjects[0]
            except:
                pass
        delattr(self, "jobject_bytes")
        # restore make_calls objects
        self._make_calls()

    def _make_calls(self):
        """
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        pass

    @property
    def classname(self):
        """
        Returns the Java classname in dot-notation.

        :return: the Java classname
        :rtype: str
        """
        return self.jobject.getClass().getName()

    def _get_property_path(self):
        if self._property_path is None:
            self._property_path = JClass("weka.core.PropertyPath")
        return self._property_path

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
        self._get_property_path().setValue(self.jobject, path, jobject)

    def get_property(self, path):
        """
        Attempts to get the value (jobject, a Java object) of the provided (bean) property path.

        :param path: the property path, e.g., "filter" for a setFilter(...)/getFilter() method pair
        :type path: str
        :return: the wrapped Java object
        :rtype: JavaObject
        """
        return JavaObject(self._get_property_path().getValue(self.jobject, path))

    @property
    def jclass(self):
        """
        Returns the Java class object of the underlying Java object.

        :return: the Java class
        :rtype: JClass
        """
        return self.jobject.getClass()

    @property
    def jwrapper(self):
        """
        Returns a JWrapper instance of the encapsulated Java object, giving access to methods
        using dot notation.

        :return: the wrapper
        """
        return self.jobject

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
    def check_type(cls, jobject, intf_or_class):
        """
        Returns whether the object implements the specified interface or is a subclass.

        :param jobject: the Java object to check
        :type jobject: JB_Object
        :param intf_or_class: the classname in Java notation (eg "weka.core.DenseInstance;")
        :type intf_or_class: str
        :return: whether object implements interface or is subclass
        :rtype: bool
        """
        return is_instance_of(jobject, intf_or_class)
        
    @classmethod
    def enforce_type(cls, jobject, intf_or_class):
        """
        Raises an exception if the object does not implement the specified interface or is not a subclass. 

        :param jobject: the Java object to check
        :type jobject: JB_Object
        :param intf_or_class: the classname in Java notation (eg "weka.core.DenseInstance")
        :type intf_or_class: str
        """
        if not cls.check_type(jobject, intf_or_class):
            raise TypeError("Object does not implement or subclass " + intf_or_class + ": " + get_classname(jobject))

    @classmethod
    def new_instance(cls, classname, options=None):
        """
        Creates a new object from the given classname using the default constructor, None in case of error.

        :param classname: the classname in Java notation (eg "weka.core.DenseInstance")
        :type classname: str
        :param options: the list of options to use, ignored if None
        :type options: list
        :return: the Java object
        :rtype: JB_Object
        """
        try:
            if options is None:
                options = []
            return JClass("weka.core.Utils").forName(JClass("java.lang.Object"), classname, options)
        except JException as e:
            print("Failed to instantiate " + classname + ": " + str(e))
            suggestions = suggest_package(classname, exact=True)
            if len(suggestions) > 0:
                if jvm.automatically_install_packages:
                    if len(suggestions) > 1:
                        print("More than one package (%s) contains class (%s), cannot install automatically!" % (classname, ", ".join(suggestions)))
                    elif len(suggestions) == 1:
                        from weka.core.packages import install_package
                        for suggestion in suggestions:
                            print("Installing package: %s" % suggestion)
                            install_package(suggestion)
                        print("Please restart script to take advantage of newly installed packages. Exiting now...")
                        jvm.stop()
                        sys.exit(0)
                else:
                    print("Class '" + classname + "' is available from package: " + ", ".join(suggestions))
                    if not jvm.with_package_support:
                        print("Also, you need to start up the JVM with package support:\njvm.start(packages=True)")
            else:
                if not jvm.with_package_support:
                    print("If this class is from a Weka package, then you need to start up the JVM with package support:\njvm.start(packages=True)")
            return None


class Environment(JavaObject):
    """
    Wraps around weka.core.Environment
    """

    def __init__(self, jobject=None):
        """
        Initializes the object.

        :param jobject: the environment java object to use
        :type jobject: JB_Object
        """
        if jobject is None:
            jobject = JClass("weka.core.Environment")()
        else:
            Environment.enforce_type(jobject, "weka.core.Environment")
        super(Environment, self).__init__(jobject)

    def add_variable(self, key, value, system_wide=False):
        """
        Adds the environment variable.

        :param key: the name of the variable
        :type key: str
        :param value: the value
        :type value: str
        :param system_wide: whether to add the variable system wide
        :type system_wide: bool
        """
        if system_wide:
            self.jobject.addVariableSystemWide(key, value)
        else:
            self.jobject.addVariable(key, value)

    def remove_variable(self, key):
        """
        Adds the environment variable.

        :param key: the name of the variable
        :type key: str
        """
        self.jobject.removeVariable(key)

    def variable_value(self, key):
        """
        Returns the value of the environment variable.

        :param key: the name of the variable
        :type key: str
        :return: the variable value
        :rtype: str
        """
        return self.jobject.getVariableValue(key)

    def variable_names(self):
        """
        Returns the names of all environment variables.

        :return: the names of the variables
        :rtype: list
        """
        result = []
        names = self.jobject.getVariableNames()
        for name in names:
            result.append(str(name))
        return result

    @classmethod
    def system_wide(cls):
        """
        Returns the system-wide environment.

        ;return: the environment
        :rtype: Environment
        """
        return Environment(jobject=JClass("weka.core.Environment").getSystemWide())


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

    def __len__(self):
        """
        Returns the length of the array.

        :return: the array length
        :rtype: int
        """
        return len(self.jobject)

    def __init__(self, jobject):
        """
        Initializes the wrapper with the specified Java object.

        :param jobject: the java array object to wrap
        :type jobject: JB_Object
        """
        super(JavaArray, self).__init__(jobject)
        c = self.jclass
        if not c.isArray():
            raise Exception("Not an array!")

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
        element = self.jobject[key]
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
        self.jobject[key] = obj

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

    def __str__(self):
        """
        Returns a short description of itself.
        """
        return "%s[%d]" % (self.component_type(), len(self))

    def __repr__(self):
        """
        Just returns the representation from __str__.

        :return: the representation
        :rtype: str
        """
        return self.__str__()

    def component_type(self):
        """
        Returns the classname of the elements.

        :return: the class of the elements
        :rtype: str
        """
        return self.jobject.getClass().getComponentType().getName()

    @classmethod
    def new_array(cls, classname, length):
        """
        Creates a new array with the given classname and length; initial values are null.

        :param classname: the classname in Java notation (eg "weka.core.DenseInstance")
        :type classname: str
        :param length: the length of the array
        :type length: int
        :return: the Java array
        :rtype: JB_Object
        """
        return new_array(classname, length)


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
            if enum is None:
                raise Exception("Enum member cannot be None if no JB_Object instance provided!")
            jobject = get_enum(enum, member)
        super(Enum, self).__init__(jobject)

    @property
    def name(self):
        """
        Returns the name of the enum member.

        :return: the name
        :rtype: str
        """
        return self.jobject.name()

    @property
    def ordinal(self):
        """
        Returns the ordinal of the enum member.

        :return: the ordinal
        :rtype: int
        """
        return self.jobject.ordinal()

    @property
    def values(self):
        """
        Returns list of all enum members.

        :return: all enum members
        :rtype: list
        """
        classname = self.jobject.getClass().getName()
        l = typeconv.from_jobject_array(JClass(classname).values())
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
        super(Random, self).__init__(JClass("java.util.Random")(seed))

    def next_int(self, n=None):
        """
        Next random integer. if n is provided, then between 0 and n-1.

        :param n: the upper limit (minus 1) for the random integer
        :type n: int
        :return: the next random integer
        :rtype: int
        """
        if n is None:
            return self.jobject.nextInt()
        else:
            return self.jobject.nextInt(n)

    def next_double(self):
        """
        Next random double.

        :return: the next random double
        :rtype: double
        """
        return self.jobject.nextDouble()


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
        return self.jobject.name()

    @property
    def description(self):
        """
        Returns the description of the option.

        :return: the description
        :rtype: str
        """
        return self.jobject.description()

    @property
    def synopsis(self):
        """
        Returns the synopsis of the option.

        :return: the synopsis
        :rtype: str
        """
        return self.jobject.synopsis()

    @property
    def num_arguments(self):
        """
        Returns the synopsis of the option.

        :return: the synopsis
        :rtype: str
        """
        return self.jobject.numArguments()


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
            return self.jobject.globalInfo()
        except JException:
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
            return typeconv.jstring_array_to_list(self.jobject.getOptions())
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
            self.jobject.setOptions(typeconv.string_list_to_jarray(options))

    def to_commandline(self):
        """
        Generates a commandline string from the JavaObject instance.

        :return: the commandline string
        :rtype: str
        """
        return JClass("weka.core.Utils").toCommandLine(self.jobject)

    def to_help(self, title=True, description=True, options=True, use_headers=True, separator=""):
        """
        Returns a string that contains the 'global_info' text and the options.

        :param title: whether to output a title
        :type title: bool
        :param description: whether to output the description
        :type description: bool
        :param options: whether to output the options
        :type options: bool
        :param use_headers: whether to output headers, describing the sections
        :type use_headers: bool
        :param separator: the separator line to use between sections
        :type separator: str
        :return: the generated help string
        :rtype: str
        """
        result = []
        if title:
            result.append(self.classname)
            result.append("=" * len(self.classname))
            result.append(separator)
        if description:
            if use_headers:
                result.append("DESCRIPTION")
                result.append("")
            result.append(self.global_info())
            result.append(separator)
        if options:
            if use_headers:
                result.append("OPTIONS")
                result.append("")
            for o in self.jobject.listOptions():
                opt = Option(o)
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
        return str(self.jobject)

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
                jobject = JClass("weka.core.SingleIndex")()
            else:
                jobject = JClass("weka.core.SingleIndex")(index)
        else:
            self.enforce_type(jobject, "weka.core.SingleIndex")
        super(SingleIndex, self).__init__(jobject)

    def upper(self, upper):
        """
        Sets the upper limit.

        :param upper: the upper limit
        :type upper: int
        """
        self.jobject.setUpper(upper)

    def index(self):
        """
        Returns the integer index.

        :return: the 0-based integer index
        :rtype: int
        """
        return self.jobject.getIndex()

    @property
    def single_index(self):
        """
        Returns the string index.

        :return: the 1-based string index
        :rtype: str
        """
        return self.jobject.getSingleIndex()

    @single_index.setter
    def single_index(self, index):
        """
        Sets the string index.

        :param index: the 1-based string index
        ::type index: str
        """
        self.jobject.setSingleIndex(index)


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
                jobject = JClass("weka.core.Range")()
            else:
                jobject = JClass("weka.core.Range")(ranges)
        else:
            self.enforce_type(jobject, "weka.core.Range")
        super(Range, self).__init__(jobject)

    def upper(self, upper):
        """
        Sets the upper limit.

        :param upper: the upper limit
        :type upper: int
        """
        self.jobject.setUpper(upper)

    def selection(self):
        """
        Returns the selection list.

        :return: the list of 0-based integer indices
        :rtype: list
        """
        return list(typeconv.jint_array_to_ndarray(self.jobject.getSelection()))

    @property
    def ranges(self):
        """
        Returns the string range.

        :return: the string range of 1-based indices
        :rtype: str
        """
        return self.jobject.getRanges()

    @ranges.setter
    def ranges(self, rng):
        """
        Sets the string range.

        :param rng: the range to set
        :type rng: str
        """
        self.jobject.setRanges(rng)

    @property
    def invert(self):
        """
        Returns whether the range is inverted.

        :return: true if inverted
        :rtype: bool
        """
        return self.jobject.getInvert()

    @invert.setter
    def invert(self, invert):
        """
        Sets the invert state.

        :param invert: whether to invert or not
        :type invert: bool
        """
        self.jobject.setInvert(invert)


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
            jobject = JClass("weka.core.Tag")(ident, ident_str, readable, uppercase)
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
        return self.jobject.getID()

    @ident.setter
    def ident(self, value):
        """
        Sets the integer ID of the tag.

        :param value: the new ID
        :type value: int
        """
        self.jobject.setID(value)

    @property
    def identstr(self):
        """
        Returns the current ID string.

        :return: the ID string
        :rtype: str
        """
        return self.jobject.getIDStr()

    @identstr.setter
    def identstr(self, value):
        """
        Sets the ID string.

        :param value: the new ID string
        :type value: str
        """
        self.jobject.setIDStr(value)

    @property
    def readable(self):
        """
        Returns the 'human readable' string.

        :return: the readable string
        :rtype: str
        """
        return self.jobject.getReadable()

    @readable.setter
    def readable(self, value):
        """
        Sets the 'human readable' string.

        :param value: the new readable string
        :type value: str
        """
        self.jobject.setReadable(value)


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
            jarray = JavaArray(JavaArray.new_array("weka.core.Tag", len(tags)))
            for i in range(len(tags)):
                jarray[i] = tags[i]
            jobject = jarray.jobject
        self.enforce_type(jobject, "weka.core.Tag")
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
        return Tags(jobject=get_static_field(classname, field))

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
        func = getattr(javaobject.jobject, methodname)
        return Tags(jobject=func())


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
                jobject = JClass("weka.core.SelectedTag")(tag_text, tobj)
            else:
                jobject = JClass("weka.core.SelectedTag")(tag_id, tobj)
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
        return Tag(self.jobject.getSelectedTag())

    @property
    def tags(self):
        """
        Returns the associated tags.

        :return: the list of Tag objects
        :rtype: list
        """
        result = []
        a = self.jobject.getTags()
        for i in range(len(a)):
            result.append(Tag(str(a[i])))
        return result


def join_options(options):
    """
    Turns the list of options back into a single commandline string.

    :param options: the list of options to process
    :type options: list
    :return: the combined options
    :rtype: str
    """
    return JClass("weka.core.Utils").joinOptions(typeconv.string_list_to_jarray(options))


def split_options(cmdline):
    """
    Splits the commandline into a list of options.

    :param cmdline: the commandline string to split into individual options
    :type cmdline: str
    :return: the split list of commandline options
    :rtype: list
    """
    return typeconv.jstring_array_to_list(JClass("weka.core.Utils").splitOptions(cmdline))


def split_commandline(cmdline):
    """
    Splits the commandline string into classname and options list.

    :param cmdline: the commandline string to split
    :type cmdline: str
    :return: the tuple of classname and options list
    :rtype: tuple
    """
    options = split_options(cmdline)
    clsname = options[0]
    options.pop(0)
    return clsname, options


def backquote(s):
    """
    Backquotes the string.

    :param s: the string to process
    :type s: str
    :return: the backquoted string
    :rtype: str
    """
    return JClass("weka.core.Utils").backQuoteChars(s)


def unbackquote(s):
    """
    Un-backquotes the string.

    :param s: the string to process
    :type s: str
    :return: the un-backquoted string
    :rtype: str
    """
    return JClass("weka.core.Utils").unbackQuoteChars(s)


def quote(s):
    """
    Quotes the string if necessary.

    :param s: the string to process
    :type s: str
    :return: the quoted string
    :rtype: str
    """
    return JClass("weka.core.Utils").quote(s)


def unquote(s):
    """
    Un-quotes the string.

    :param s: the string to process
    :type s: str
    :return: the un-quoted string
    :rtype: str
    """
    return JClass("weka.core.Utils").unquote(s)


def to_commandline(optionhandler):
    """
    Generates a commandline string from the OptionHandler instance.

    :param optionhandler: the OptionHandler instance to turn into a commandline
    :type optionhandler: OptionHandler
    :return: the commandline string
    :rtype: str
    """
    return JClass("weka.core.Utils").toCommandLine(optionhandler.jobject)


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
    cls, params = split_commandline(cmdline)
    handler = OptionHandler(JClass("weka.core.Utils").forName(JClass("java.lang.Object"), cls, params))
    if classname is None:
        return handler
    else:
        c = get_class(classname)
        return c(jobject=handler.jobject)


def complete_classname(classname):
    """
    Attempts to complete a partial classname like '.J48' and returns the full
    classname if a single match was found, otherwise an exception is raised.

    :param classname: the partial classname to expand
    :type classname: str
    :return: the full classname
    :rtype: str
    """

    result = JClass("weka.Run").findSchemeMatch(classname, True)
    if len(result) == 1:
        return str(result[0])
    elif len(result) == 0:
        raise Exception("No classname matches found for: " + classname)
    else:
        matches = []
        for i in range(len(result)):
            matches.append(str(result[i]))
        raise Exception("Found multiple matches for '" + classname + "':\n" + '\n'.join(matches))


def help_for(classname, title=True, description=True, options=True, use_headers=True, separator=""):
    """
    Generates a help screen for the specified class.

    :param classname: the class to get the help screen for, must implement the OptionHandler interface
    :type classname: str
    :param title: whether to output a title
    :type title: bool
    :param description: whether to output the description
    :type description: bool
    :param options: whether to output the options
    :type options: bool
    :param use_headers: whether to output headers, describing the sections
    :type use_headers: bool
    :param separator: the separator line to use between sections
    :type separator: str
    :return: the help screen, None if not available
    :rtype: str
    """
    try:
        obj = JavaObject.new_instance(classname)
        if is_instance_of(obj, "weka.core.OptionHandler"):
            handler = OptionHandler(jobject=obj)
            return handler.to_help(title=title, description=description, options=options,
                                   use_headers=use_headers, separator=separator)
        else:
            return None
    except Exception:
        return None


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
        return self.jobject.getProperty()

    @prop.setter
    def prop(self, s):
        """
        Sets the property to apply the parameter to.

        :param s: the property
        :type s: str
        """
        self.jobject.setProperty(s)


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
        return split_options(self.jobject.getList())

    @values.setter
    def values(self, l):
        """
        Sets the list of values to apply.

        :param l: the list of values (strings)
        :type l: list
        """
        self.jobject.setList(join_options(l))


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
            jobject = MathParameter.new_instance(classname)
        self.enforce_type(jobject, "weka.core.setupgenerator.MathParameter")
        super(MathParameter, self).__init__(jobject=jobject, options=options)

    @property
    def minimum(self):
        """
        Returns the currently set minimum value.

        :return: the minimum
        :rtype: float
        """
        return self.jobject.getMin()

    @minimum.setter
    def minimum(self, m):
        """
        Sets the new minimum value.

        :param m: the minimum
        :type m: float
        """
        self.jobject.setMin(m)

    @property
    def maximum(self):
        """
        Returns the currently set maximum value.

        :return: the maximum
        :rtype: float
        """
        return self.jobject.getMax()

    @maximum.setter
    def maximum(self, m):
        """
        Sets the new maximum value.

        :param m: the maximum
        :type m: float
        """
        self.jobject.setMax(m)

    @property
    def step(self):
        """
        Returns the currently set step value.

        :return: the step
        :rtype: float
        """
        return self.jobject.getStep()

    @step.setter
    def step(self, s):
        """
        Sets the new step value.

        :param s: the step
        :type s: float
        """
        self.jobject.setStep(s)

    @property
    def base(self):
        """
        Returns the currently set base value.

        :return: the base
        :rtype: float
        """
        return self.jobject.getBase()

    @base.setter
    def base(self, b):
        """
        Sets the new base value.

        :param b: the base
        :type b: float
        """
        self.jobject.setBase(b)

    @property
    def expression(self):
        """
        Returns the currently set expression.

        :return: the expression
        :rtype: str
        """
        return self.jobject.getExpression()

    @expression.setter
    def expression(self, e):
        """
        Sets the new expression.

        :param e: the expression
        :type e: str
        """
        self.jobject.setExpression(e)


class SetupGenerator(OptionHandler):
    """
    Allows generation of large number of setups using parameter setups.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the specified setup generator.

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
        jobj = self.jobject.getBaseObject()
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
        self.jobject.setBaseObject(obj.jobject)

    @property
    def parameters(self):
        """
        Returns the list of currently set search parameters.

        :return: the list of AbstractSearchParameter objects
        :rtype: list
        """
        array = JavaArray(self.jobject.getParameters())
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
        array = JavaArray(jobject=JavaArray.new_array("weka.core.setupgenerator.AbstractParameter", len(params)))
        for idx, obj in enumerate(params):
            array[idx] = obj.jobject
        self.jobject.setParameters(array.jobject)

    def setups(self):
        """
        Generates and returns all the setups according to the parameter search space.

        :return: the list of configured objects (of type JavaObject)
        :rtype: list
        """
        result = []
        has_options = self.base_object.is_optionhandler
        for item in self.jobject.setups():
            if has_options:
                result.append(OptionHandler(item))
            else:
                result.append(JavaObject(item))
        return result


class Date(JavaObject):
    """
    Wraps a java.util.Date object.
    """

    def __init__(self, jobject=None, msecs=None):
        """
        Initializes the specified Date. Uses the current timestamp if no jobject or msecs provided.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param msecs: the milli-seconds since 1970
        :type msecs: long
        """
        if jobject is None:
            if msecs is None:
                jobject = JClass("java.util.Date")()
            else:
                jobject = JClass("java.util.Date")(msecs)
        else:
            self.enforce_type(jobject, "java.util.Date")
        super(Date, self).__init__(jobject=jobject)

    @property
    def time(self):
        """
        Returns the stored milli-seconds.

        :return: the milli-seconds
        :rtype: long
        """
        return self.jobject.getTime()

    @time.setter
    def time(self, msecs):
        """
        Sets the milli-seconds.

        :param msecs: the milli-seconds to use
        :return:
        """
        self.jobject.setTime(msecs)


def load_suggestions():
    """
    Loads the class/package suggestions, if necessary.
    """
    global suggestions
    if suggestions is not None:
        return
    filename = jvm.lib_dir() + os.sep + "pkg_suggestions.csv"
    suggestions = {}
    with open(filename) as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if len(row[1]) > 0:
                suggestions[row[1]] = row[0]


def suggest_package(name, exact=False):
    """
    Suggests package(s) for the given name (classname, package name). Matching can be either exact or just a substring.

    :param name: the name to look for
    :type name: str
    :param exact: whether to perform exact matching or substring matching
    :type exact: bool
    :return: list of matching package names
    :rtype: list
    """

    global suggestions

    result = []

    load_suggestions()

    for cname in suggestions:
        add = False
        if exact:
            if name == cname:
                add = True
        else:
            if name in cname:
                add = True
        if add:
            pkg = suggestions[cname]
            if pkg not in result:
                result.append(pkg)

    return result


def get_non_public_field(jobject, field):
    """
    Returns the specified non-public field from the Java object.

    :param jobject: the Java object to get the field from
    :type jobject: JBObject
    :param field: the name of the field to retrieve
    :type field: str
    :return: the value
    """
    return JClass("weka.core.ClassHelper").getNonPublicField(jobject, field)


def call_non_public_method(jobject, method, arg_types=None, arg_values=None):
    """
    For calling a non-public method of the provided Java object.

    :param jobject: the Java object to call the method on
    :type jobject: JBObject
    :param method: the name of the method to call
    :type method: str
    :param arg_types: the method argument types, either Java objects or classname strings (eg "java.lang.Integer" or "int")
    :type arg_types: list
    :param arg_values: the method argument values
    :type arg_values: list
    :return: the result of the method call
    """
    # convert string classnames into Java class objects
    if arg_types is not None:
        for i in range(len(arg_types)):
            if isinstance(arg_types[i], str):
                arg_types[i] = get_jclass(arg_types[i])

    return JClass("weka.core.ClassHelper").callNonPublicMethod(jobject, method, arg_types, arg_values)


def new_array(classname, length):
    """
    Creates a new array of the specified class and length.

    :param classname: the type of the array
    :type classname: str
    :param length: the length of the array
    :type length: int
    :return: the generated array
    """
    return JClass("java.lang.reflect.Array").newInstance(get_jclass(classname=classname), length)


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
                output += 'handler = OptionHandler(JavaObject.new_array("' + cname + '"))\n'
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
