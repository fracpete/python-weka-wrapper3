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
# Copyright (C) 2015-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
from weka.core.classes import OptionHandler


class TokenIterator(object):
    """
    Iterator for string tokens.
    """
    def __init__(self, tokenizer):
        """
        Initializes the iterator.

        :param tokenizer: the tokenizer instance to use
        :type tokenizer: Tokenizer
        """
        self.tokenizer = tokenizer
        self._make_calls()

    def _make_calls(self):
        """
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        self._mc_has_more = javabridge.make_call(self.tokenizer.jobject, "hasMoreElements", "()Z")
        self._mc_next = javabridge.make_call(self.tokenizer.jobject, "nextElement", "()Ljava/lang/String;")

    def __iter__(self):
        """
        Returns itself.
        """
        return self

    def __next__(self):
        """
        Reads the next dataset row.

        :return: the next row
        :rtype: Instance
        """
        if not self._mc_has_more():
            raise StopIteration()
        else:
            return javabridge.get_env().get_string(self._mc_next())


class Tokenizer(OptionHandler):
    """
    Wrapper class for tokenizers.
    """

    def __init__(self, classname="weka.core.tokenizers.AlphabeticTokenizer", jobject=None, options=None):
        """
        Initializes the specified tokenizer using either the classname or the supplied JB_Object.

        :param classname: the classname of the tokenizer
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Tokenizer.new_instance(classname)
        self.enforce_type(jobject, "weka.core.tokenizers.Tokenizer")
        super(Tokenizer, self).__init__(jobject=jobject, options=options)

    def tokenize(self, s):
        """
        Tokenizes the string.

        :param s: the string to tokenize
        :type s: str
        :return: the iterator
        :rtype: TokenIterator
        """
        javabridge.call(self.jobject, "tokenize", "(Ljava/lang/String;)V", s)
        return TokenIterator(self)
