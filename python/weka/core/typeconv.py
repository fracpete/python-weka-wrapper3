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

# typeconv.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
import numpy

# logging setup
logger = logging.getLogger(__name__)


def jstring_array_to_list(a):
    """
    Turns the Java string array into Python unicode string list.

    :param a: the string array to convert
    :type a: JB_Object
    :return: the string list
    :rtype: list
    """
    result = []
    length = javabridge.get_env().get_array_length(a)
    wrapped = javabridge.get_env().get_object_array_elements(a)
    for i in range(length):
        result.append(javabridge.get_env().get_string(wrapped[i]))
    return result


def string_list_to_jarray(l):
    """
    Turns a Python unicode string list into a Java String array.

    :param l: the string list
    :type: list
    :rtype: java string array
    :return: JB_Object
    """
    result = javabridge.get_env().make_object_array(len(l), javabridge.get_env().find_class("java/lang/String"))
    for i in range(len(l)):
        javabridge.get_env().set_object_array_element(result, i, javabridge.get_env().new_string_utf(l[i]))
    return result


def jstring_list_to_string_list(l, return_empty_if_none=True):
    """
    Converts a Java java.util.List containing strings into a Python list.

    :param l: the list to convert
    :type l: JB_Object
    :param return_empty_if_none: whether to return an empty list or None when list object is None
    :type return_empty_if_none: bool
    :return: the list with UTF strings
    :rtype: list
    """
    result = []
    if l is None:
        if return_empty_if_none:
            return []
        else:
            return None
    objs = javabridge.get_collection_wrapper(l)
    for obj in objs:
        result.append(javabridge.get_env().get_string_utf(obj))
    return result


def jdouble_matrix_to_ndarray(m):
    """
    Turns the Java matrix (2-dim array) of doubles into a numpy 2-dim array.

    :param m: the double matrix
    :type: JB_Object
    :return: Numpy array
    :rtype: numpy.darray
    """
    rows = javabridge.get_env().get_object_array_elements(m)
    num_rows = len(rows)
    num_cols = javabridge.get_env().get_array_length(rows[0])
    result = numpy.zeros(num_rows * num_cols).reshape((num_rows, num_cols))
    i = 0
    for row in rows:
        elements = javabridge.get_env().get_double_array_elements(row)
        n = 0
        for element in elements:
            result[i][n] = element
            n += 1
        i += 1
    return result


def jenumeration_to_list(enm):
    """
    Turns the java.util.Enumeration into a list.

    :param enm: the enumeration to convert
    :type enm: JB_Object
    :return: the list
    :rtype: list
    """
    result = []
    while javabridge.call(enm, "hasMoreElements", "()Z"):
        result.append(javabridge.call(enm, "nextElement", "()Ljava/lang/Object;"))
    return result


def float_to_jfloat(d):
    """
    Turns the Python float into a Java java.lang.Float object.

    :param d: the Python float
    :type d: float
    :return: the Float object
    :rtype: JB_Object
    """
    return javabridge.make_instance("java/lang/Float", "(D)V", d)


def jdouble_to_float(d):
    """
    Turns the Java java.lang.Double object into Python float object.

    :param d: the java.lang.Double
    :type d: JB_Object
    :return: the Float object
    :rtype: float
    """
    return javabridge.call(d, "doubleValue", "()D", d)
