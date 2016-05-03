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

# stemmers.py
# Copyright (C) 2015-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import os
import weka.core.jvm as jvm
from weka.core.stemmers import Stemmer
import wekatests.tests.weka_test as weka_test


class TestStemmers(weka_test.WekaTest):

    def test_instantiation(self):
        """
        Tests instantiating a stemmer.
        """
        stemmer = Stemmer()
        self.assertIsNotNone(stemmer, msg="Stemmer should not be None")
        stemmer = Stemmer(classname="weka.core.stemmers.LovinsStemmer")
        self.assertIsNotNone(stemmer, msg="Stemmer should not be None")

    def test_stem(self):
        """
        Tests calling the "stem" method.
        """
        stemmer = Stemmer(classname="weka.core.stemmers.LovinsStemmer")
        self.assertIsNotNone(stemmer, msg="Stemmer should not be None")
        unstemmed = "filters"
        stemmed = stemmer.stem(unstemmed)
        self.assertEqual("filter", stemmed, msg="Word not stemmed: " + stemmed)

        stemmer = Stemmer(classname="weka.core.stemmers.NullStemmer")
        self.assertIsNotNone(stemmer, msg="Stemmer should not be None")
        unstemmed = "filters"
        stemmed = stemmer.stem(unstemmed)
        self.assertEqual(unstemmed, stemmed, msg="Word should not be stemmed: " + stemmed)


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestStemmers)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
