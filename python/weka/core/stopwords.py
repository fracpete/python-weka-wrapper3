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
# Copyright (C) 2015-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
from weka.core.classes import OptionHandler


class Stopwords(OptionHandler):
    """
    Wrapper class for stopwords handlers.
    """

    def __init__(self, classname="weka.core.stopwords.Null", jobject=None, options=None):
        """
        Initializes the specified stopwords handler using either the classname or the supplied JB_Object.

        :param classname: the classname of the stopwords handler
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Stopwords.new_instance(classname)
        self.enforce_type(jobject, "weka.core.stopwords.StopwordsHandler")
        super(Stopwords, self).__init__(jobject=jobject, options=options)

    def _make_calls(self):
        """
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        super(Stopwords, self)._make_calls()
        self._mc_is_stopword = javabridge.make_call(self.jobject, "isStopword", "(Ljava/lang/String;)Z")

    def is_stopword(self, s):
        """
        Checks a string whether it is a stopword.

        :param s: the string to check
        :type s: str
        :return: True if a stopword
        :rtype: bool
        """
        return self._mc_is_stopword(javabridge.get_env().new_string_utf(s))
