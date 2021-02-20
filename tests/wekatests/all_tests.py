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

# all_tests.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import wekatests.associations
import wekatests.attribute_selection
import wekatests.classifiers
import wekatests.clusterers
import wekatests.datagenerators
import wekatests.experiments
import wekatests.filters
import wekatests.timeseries
import wekatests.coretests.all_tests
import wekatests.plottests.all_tests


"""
Executes all available tests.
Add additional test suites to the `suite()` method.
"""


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    result = unittest.TestSuite()
    result.addTests(wekatests.associations.suite())
    result.addTests(wekatests.attribute_selection.suite())
    result.addTests(wekatests.classifiers.suite())
    result.addTests(wekatests.clusterers.suite())
    result.addTests(wekatests.datagenerators.suite())
    result.addTests(wekatests.experiments.suite())
    result.addTests(wekatests.filters.suite())
    result.addTests(wekatests.timeseries.suite())
    result.addTests(wekatests.coretests.all_tests.suite())
    result.addTests(wekatests.plottests.all_tests.suite())
    return result


if __name__ == '__main__':
    jvm.start(packages=True)
    unittest.TextTestRunner().run(suite())
    jvm.stop()
