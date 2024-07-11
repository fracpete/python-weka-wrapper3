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
# Copyright (C) 2014-2024 Fracpete (pythonwekawrapper at gmail dot com)

from jpype import JFloat, JString, JClass, JDouble, JInt, JObject
import logging
import numpy

# logging setup
logger = logging.getLogger(__name__)


def jstring_array_to_list(a):
    """
    Turns the Java string array into Python unicode string list.

    :param a: the string array to convert
    :type a: JPype object
    :return: the string list
    :rtype: list
    """
    return [x for x in a]


def string_list_to_jarray(l):
    """
    Turns a Python unicode string list into a Java String array.

    :param l: the string list
    :type: list
    :rtype: java string array
    :return: JPype object
    """
    result = JString[len(l)]
    for i in range(len(l)):
        result[i] = l[i]
    return result


def string_list_to_jlist(l):
    """
    Turns a Python unicode string list into a Java List.

    :param l: the string list
    :type: list
    :rtype: java list
    """
    return JClass("java.util.ArrayList")(l)


def jstring_list_to_string_list(l, return_empty_if_none=True):
    """
    Converts a Java java.util.List containing strings into a Python list.

    :param l: the list to convert
    :type l: JPype object
    :param return_empty_if_none: whether to return an empty list or None when list object is None
    :type return_empty_if_none: bool
    :return: the list with UTF strings
    :rtype: list
    """
    if l is None:
        if return_empty_if_none:
            return []
        else:
            return None
    return [x for x in l]


def jdouble_matrix_to_ndarray(m):
    """
    Turns the Java matrix (2-dim array) of doubles into a numpy 2-dim array.

    :param m: the double matrix
    :type: JPype object
    :return: Numpy array
    :rtype: numpy.darray
    """
    num_rows = len(m)
    num_cols = len(m[0])
    result = numpy.zeros(num_rows * num_cols).reshape((num_rows, num_cols))
    for row in range(num_rows):
        for col in range(num_cols):
            result[row][col] = m[row][col]
    return result


def jdouble_array_to_ndarray(a):
    """
    Turns the Java array of doubles into a numpy 2-dim array.

    :param a: the double array
    :type: JPype object
    :return: Numpy array
    :rtype: numpy.darray
    """
    result = numpy.zeros(len(a))
    for i in range(len(a)):
        result[i] = a[i]
    return result


def jint_array_to_ndarray(a):
    """
    Turns the Java array of ints into a numpy 2-dim array.

    :param a: the double array
    :type: JPype object
    :return: Numpy array
    :rtype: numpy.darray
    """
    result = numpy.zeros(len(a))
    for i in range(len(a)):
        result[i] = a[i]
    return result


def jenumeration_to_list(enm):
    """
    Turns the java.util.Enumeration into a list.

    :param enm: the enumeration to convert
    :type enm: JPype object
    :return: the list
    :rtype: list
    """
    return [x for x in enm]


def float_to_jfloat(d):
    """
    Turns the Python float into a Java java.lang.Float object.

    :param d: the Python float
    :type d: float
    :return: the Float object
    :rtype: JPype object
    """
    return JFloat(d)


def jdouble_to_float(d):
    """
    Turns the Java java.lang.Double object into Python float object.

    :param d: the java.lang.Double
    :type d: JPype object
    :return: the Float object
    :rtype: float
    """
    return float(d)


def to_string(o):
    """
    Turns the object into a string.

    :param o: the object to convert
    :return: the generated string
    :rtype: str
    """
    if o is None:
        return None

    result = str(o)

    if isinstance(o, bytes):
        try:
            result = o.decode("utf-8")
        except:
            pass

    return result


def to_jdouble_array(values, none_as_nan: bool = False):
    """
    Converts the list of floats or the numpy array into a Java array.

    :param values: the values to convert
    :param none_as_nan: whether to convert None values to NaN
    :type none_as_nan: bool
    :return: the java array
    """
    result = JDouble[len(values)]
    nan = float("nan")
    for i in range(len(values)):
        if none_as_nan and (values[i] is None):
            result[i] = nan
        elif values[i] == numpy.nan:
            result[i] = nan
        else:
            result[i] = values[i]
    return result


def to_jint_array(values):
    """
    Converts the list of ints into a Java array.

    :param values: the values to convert
    :return: the java array
    """
    result = JInt[len(values)]
    for i in range(len(values)):
        result[i] = values[i]
    return result


def to_jobject_array(values):
    """
    Converts the list of objects into a Java object array.

    :param values: the list of objects to convert
    :return: the java array
    """
    result = JObject[len(values)]
    for i in range(len(values)):
        result[i] = values[i]
    return result


def from_jobject_array(a):
    """
    Converts the java object array into a list.

    :param a: the java array to convert
    :return: the generated list
    """
    result = []
    for i in range(len(a)):
        result.append(a[i])
    return result
