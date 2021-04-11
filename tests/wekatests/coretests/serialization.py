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

import unittest
import tempfile
import javabridge
import os
import weka.core.jvm as jvm
import weka.core.typeconv as typeconv
import wekatests.tests.weka_test as weka_test
from weka.core.classes import serialization_read, serialization_write, serialization_read_all, serialization_write_all


class TestSerialization(weka_test.WekaTest):

    def test_read_write(self):
        """
        Tests methods read and write.
        """
        fname = self.tempfile("readwrite.ser")
        self.delfile(fname)

        lin = ["A", "B", "C", "D"]
        vin = javabridge.make_instance("java/util/Vector", "()V")
        for element in lin:
            javabridge.call(vin, "add", "(Ljava/lang/Object;)Z", element)
        serialization_write(fname, vin)
        self.assertTrue(os.path.exists(fname), msg="Failed to write to " + fname + "?")

        vout = serialization_read(fname)
        self.assertIsNotNone(vout, msg="Failed to read from " + fname + "?")
        enm = javabridge.call(vin, "elements", "()Ljava/util/Enumeration;")
        lout = typeconv.jenumeration_to_list(enm)
        self.delfile(fname)
        self.assertEqual(lin, lout, msg="Input/output differ")

    def test_read_write_all(self):
        """
        Tests methods read_all and write_all.
        """
        fname = self.tempfile("readwrite.ser")
        self.delfile(fname)

        lin = []
        for i in range(4):
            lin.append(javabridge.make_instance("java/lang/Integer", "(I)V", i))
        serialization_write_all(fname, lin)
        self.assertTrue(os.path.exists(fname), msg="Failed to write to " + fname + "?")

        lout = serialization_read_all(fname)
        self.assertIsNotNone(lout, msg="Failed to read from " + fname + "?")
        self.delfile(fname)
        self.assertEqual(len(lin), len(lout), msg="Number of elements differ")
        for i in range(len(lin)):
            iin = javabridge.call(lin[i], "intValue", "()I")
            iout = javabridge.call(lout[i], "intValue", "()I")
            self.assertEqual(iin, iout, msg="Input/output differ at #" + str(i))


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestSerialization)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
