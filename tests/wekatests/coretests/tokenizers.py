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

# tokenizers.py
# Copyright (C) 2015-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import os
import weka.core.jvm as jvm
from weka.core.tokenizers import Tokenizer
import wekatests.tests.weka_test as weka_test


class TestTokenizer(weka_test.WekaTest):

    def test_instantiation(self):
        """
        Tests instantiating a tokenizers handle.
        """
        tokenizer = Tokenizer()
        self.assertIsNotNone(tokenizer, msg="Tokenizer should not be None")
        tokenizer = Tokenizer(classname="weka.core.tokenizers.WordTokenizer")
        self.assertIsNotNone(tokenizer, msg="Tokenizer should not be None")

    def test_tokenize(self):
        """
        Tests calling the "tokenize" method.
        """
        tokenizer = Tokenizer(classname="weka.core.tokenizers.WordTokenizer")
        self.assertIsNotNone(tokenizer, msg="Tokenizer should not be None")
        sentence = "The quick brown fox jumps over the lazy dog"
        words = list(tokenizer.tokenize(sentence))
        self.assertEqual([u'The', u'quick', u'brown', u'fox', u'jumps', u'over', u'the', u'lazy', u'dog'], words, msg="Tokens differ")


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestTokenizer)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
