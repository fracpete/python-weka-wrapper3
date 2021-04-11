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
# Copyright (C) 2015-2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
from weka.core.classes import OptionHandler


class Stemmer(OptionHandler):
    """
    Wrapper class for stemmers.
    """

    def __init__(self, classname="weka.core.stemmers.NullStemmer", jobject=None, options=None):
        """
        Initializes the specified stemmer using either the classname or the supplied JB_Object.

        :param classname: the classname of the stemmer
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Stemmer.new_instance(classname)
        self.enforce_type(jobject, "weka.core.stemmers.Stemmer")
        super(Stemmer, self).__init__(jobject=jobject, options=options)

    def _make_calls(self):
        """
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        super(Stemmer, self)._make_calls()
        self._mc_stem = javabridge.make_call(self.jobject, "stem", "(Ljava/lang/String;)Ljava/lang/String;")

    def stem(self, s):
        """
        Performs stemming on the string.

        :param s: the string to stem
        :type s: str
        :return: the stemmed string
        :rtype: str
        """
        return javabridge.get_env().get_string(self._mc_stem(javabridge.get_env().new_string_utf(s)))
