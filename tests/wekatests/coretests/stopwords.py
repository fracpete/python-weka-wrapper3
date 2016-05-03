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

# stopwords.py
# Copyright (C) 2015-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import os
import weka.core.jvm as jvm
from weka.core.stopwords import Stopwords
import wekatests.tests.weka_test as weka_test


class TestStopwords(weka_test.WekaTest):

    def test_instantiation(self):
        """
        Tests instantiating a stopwords handle.
        """
        stopwords = Stopwords()
        self.assertIsNotNone(stopwords, msg="Stopwords should not be None")
        stopwords = Stopwords(classname="weka.core.stopwords.Rainbow")
        self.assertIsNotNone(stopwords, msg="Stopwords should not be None")

    def test_is_stopword(self):
        """
        Tests calling the "is_stopword" method.
        """
        stopwords = Stopwords(classname="weka.core.stopwords.Rainbow")
        self.assertIsNotNone(stopwords, msg="Stopwords should not be None")
        word = "the"
        is_stopword = stopwords.is_stopword(word)
        self.assertEqual(True, is_stopword, msg="Should be stopword")
        word = "word"
        is_stopword = stopwords.is_stopword(word)
        self.assertEqual(False, is_stopword, msg="Should not be stopword")


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestStopwords)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
