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

import unittest
import weka.core.jvm as jvm
import weka.core.typeconv as typeconv
import wekatests.tests.weka_test as weka_test
from jpype import JClass


class TestTypes(weka_test.WekaTest):

    def test_string_list_conversions(self):
        """
        Tests methods string_list_to_jarray and jstring_array_to_list.
        """
        lin = ["A", "B", "C", "D"]
        a = typeconv.string_list_to_jarray(lin)
        lout = typeconv.jstring_array_to_list(a)
        self.assertEqual(lin, lout, msg="Elements differ")

    def test_enumeration_to_list(self):
        """
        Tests method enumeration_to_list.
        """
        lin = ["A", "B", "C", "D"]
        v = JClass("java.util.Vector")()
        for element in lin:
            v.add(element)
        lout = typeconv.jenumeration_to_list(v.elements())
        self.assertEqual(lin, lout, msg="Elements differ")


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestTypes)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
