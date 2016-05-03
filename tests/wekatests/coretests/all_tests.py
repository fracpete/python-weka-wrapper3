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
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import wekatests.coretests.capabilities
import wekatests.coretests.classes
import wekatests.coretests.converters
import wekatests.coretests.dataset
import wekatests.coretests.serialization
import wekatests.coretests.stemmers
import wekatests.coretests.stopwords
import wekatests.coretests.tokenizers
import wekatests.coretests.typeconv
import wekatests.coretests.version


"""
Executes all available tests for `weka.core`.
Add additional test suites to the `suite()` method.
"""


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    result = unittest.TestSuite()
    result.addTests(wekatests.coretests.capabilities.suite())
    result.addTests(wekatests.coretests.classes.suite())
    result.addTests(wekatests.coretests.converters.suite())
    result.addTests(wekatests.coretests.dataset.suite())
    result.addTests(wekatests.coretests.serialization.suite())
    result.addTests(wekatests.coretests.stemmers.suite())
    result.addTests(wekatests.coretests.stopwords.suite())
    result.addTests(wekatests.coretests.tokenizers.suite())
    result.addTests(wekatests.coretests.typeconv.suite())
    result.addTests(wekatests.coretests.version.suite())
    return result


if __name__ == '__main__':
    jvm.start(packages=True)
    unittest.TextTestRunner().run(suite())
    jvm.stop()
