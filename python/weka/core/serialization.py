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

# serialization.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import weka.core.classes as classes
from weka.core.classes import JavaObject
from javabridge.jutil import JavaException

# logging setup
logger = logging.getLogger(__name__)


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
        serialized = javabridge.make_instance("weka/core/SerializedObject", "(Ljava/lang/Object;)V", jobject)
        jcopy = javabridge.call(serialized, "getObject", "()Ljava/lang/Object;")
        if wrapped:
            jcopy = obj.__class__(jobject=jcopy)
        return jcopy
    except JavaException as e:
        print("Failed to create copy of " + classes.get_classname(obj) + ": " + str(e))
        return None


def read(filename):
    """
    Reads the serialized object from disk. Caller must wrap object in appropriate Python wrapper class.

    :param filename: the file with the serialized object
    :type filename: str
    :return: the JB_Object
    :rtype: JB_Object
    """
    return javabridge.static_call(
        "Lweka/core/SerializationHelper;", "read",
        "(Ljava/lang/String;)Ljava/lang/Object;",
        filename)


def read_all(filename):
    """
    Reads the serialized objects from disk. Caller must wrap objects in appropriate Python wrapper classes.

    :param filename: the file with the serialized objects
    :type filename: str
    :return: the list of JB_OBjects
    :rtype: list
    """
    array = javabridge.static_call(
        "Lweka/core/SerializationHelper;", "readAll",
        "(Ljava/lang/String;)[Ljava/lang/Object;",
        filename)
    if array is None:
        return None
    else:
        return javabridge.get_env().get_object_array_elements(array)


def write(filename, jobject):
    """
    Serializes the object to disk. JavaObject instances get automatically unwrapped.

    :param filename: the file to serialize the object to
    :type filename: str
    :param jobject: the object to serialize
    :type jobject: JB_Object or JavaObject
    """
    if isinstance(jobject, JavaObject):
        jobject = jobject.jobject
    javabridge.static_call(
        "Lweka/core/SerializationHelper;", "write",
        "(Ljava/lang/String;Ljava/lang/Object;)V",
        filename, jobject)


def write_all(filename, jobjects):
    """
    Serializes the list of objects to disk. JavaObject instances get automatically unwrapped.

    :param filename: the file to serialize the object to
    :type filename: str
    :param jobjects: the list of objects to serialize
    :type jobjects: list
    """
    array = javabridge.get_env().make_object_array(len(jobjects), javabridge.get_env().find_class("java/lang/Object"))
    for i in range(len(jobjects)):
        obj = jobjects[i]
        if isinstance(obj, JavaObject):
            obj = obj.jobject
        javabridge.get_env().set_object_array_element(array, i, obj)
    javabridge.static_call(
        "Lweka/core/SerializationHelper;", "writeAll",
        "(Ljava/lang/String;[Ljava/lang/Object;)V",
        filename, array)


def to_byte_array(jobjects):
    """
    Serializes the list of objects into a numpy array.

    :param jobjects: the list of objects to serialize
    :type jobjects: list
    :return: the numpy array
    :rtype: ndarray
    """
    array = javabridge.get_env().make_object_array(len(jobjects), javabridge.get_env().find_class("java/lang/Object"))
    for i in range(len(jobjects)):
        obj = jobjects[i]
        if isinstance(obj, JavaObject):
            obj = obj.jobject
        javabridge.get_env().set_object_array_element(array, i, obj)
    return javabridge.static_call(
        "Lweka/core/PickleHelper;", "toByteArray",
        "([Ljava/lang/Object;)[B",
        array)


def from_byte_array(array):
    """
    Deserializes Java objects from the numpy array.

    :param array: the numpy array to deserialize the Java objects from
    :type array: ndarray
    :return: the list of deserialized JB_Object instances
    :rtype: list
    """
    byte_array = javabridge.get_env().make_byte_array(array)
    obj_array = javabridge.static_call(
        "Lweka/core/PickleHelper;", "fromByteArray",
        "([B)[Ljava/lang/Object;",
        byte_array)
    return javabridge.get_env().get_object_array_elements(obj_array)
