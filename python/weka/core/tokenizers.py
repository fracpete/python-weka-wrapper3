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
# Copyright (C) 2015-2024 Fracpete (pythonwekawrapper at gmail dot com)

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
        Method for obtaining method instances for faster access.
        Members must start with "_mc_"
        """
        self._mc_has_more = self.tokenizer.jobject.hasMoreElements
        self._mc_next = self.tokenizer.jobject.nextElement

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
            return self._mc_next()


class Tokenizer(OptionHandler):
    """
    Wrapper class for tokenizers.
    """

    def __init__(self, classname="weka.core.tokenizers.AlphabeticTokenizer", jobject=None, options=None):
        """
        Initializes the specified tokenizer using either the classname or the supplied JPype object.

        :param classname: the classname of the tokenizer
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        self.jobject.tokenize(s)
        return TokenIterator(self)
