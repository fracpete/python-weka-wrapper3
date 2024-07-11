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

# utils.py
# Copyright (C) 2024 Fracpete (pythonwekawrapper at gmail dot com)

from jpype import JClass
import weka.core.typeconv as typeconv
import logging

# logging setup
logger = logging.getLogger("weka.core.utils")


def correlation(values1, values2):
    """
    Computes the correlation between the two lists of floats.

    :param values1: the first list of floats
    :type values1: list
    :param values2: the second list of floats
    :type values2: list
    :return: the correlation coefficient
    :rtype: float
    """
    if len(values1) != len(values2):
        raise Exception("Lists differ in length: %d != %d" % (len(values1), len(values2)))
    return JClass("weka.core.Utils").correlation(
        typeconv.to_jdouble_array(values1, none_as_nan=True),
        typeconv.to_jdouble_array(values2, none_as_nan=True),
        len(values1))


def variance(values):
    """
    Computes the variance for a list of floats.

    :param values: the list of floats to compute the variance for
    :type values: list
    :return: the variance
    :rtype: float
    """
    return JClass("weka.core.Utils").variance(typeconv.to_jdouble_array(values, none_as_nan=True))


def normalize(values, sum_=None):
    """
    Normalizes the doubles in the array using the given value.

    :param values: the list of floats to normalize
    :type values: list
    :param sum_: the value by which the floats are to be normalized
    :type sum_: float
    :return: the normalized float values
    :rtype: list
    """
    jvalues = typeconv.to_jdouble_array(values, none_as_nan=True)
    if sum_ is None:
        JClass("weka.core.Utils").normalize(jvalues)
    else:
        JClass("weka.core.Utils").normalize(jvalues, sum_)
    return [float(x) for x in jvalues]
