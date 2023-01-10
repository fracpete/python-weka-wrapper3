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

# conversion.py
# Copyright (C) 2015-2023 Fracpete (pythonwekawrapper at gmail dot com)


from simflow.conversion import Conversion
import weka.core.classes as classes


class AnyToCommandline(Conversion):
    """
    Generates a commandline string, e.g., from a classifier.
    """

    def __init__(self, config=None):
        """
        Initializes the conversion.

        :param config: dictionary of options to use
        :type config: dict
        """
        super(AnyToCommandline, self).__init__(config=config)

    def description(self):
        """
        Returns the description for the conversion.

        :return: the description
        :rtype: str
        """
        return "Generates a commandline string, e.g., from a classifier."

    def convert(self):
        """
        Performs the actual conversion.

        :return: None if successful, otherwise errors message
        :rtype: str
        """
        self._output = classes.to_commandline(self._input)
        return None


class CommandlineToAny(Conversion):
    """
    Generates an object from a commandline string, e.g., from a classifier setup.
    """

    def __init__(self, config=None):
        """
        Initializes the conversion.

        :param config: dictionary of options to use
        :type config: dict
        """
        super(CommandlineToAny, self).__init__(config=config)

    def description(self):
        """
        Returns the description for the conversion.

        :return: the description
        :rtype: str
        """
        return "Generates an object from a commandline string, e.g., from a classifier setup."

    def fix_config(self, options):
        """
        Fixes the options, if necessary. I.e., it adds all required elements to the dictionary.

        :param options: the options to fix
        :type options: dict
        :return: the (potentially) fixed options
        :rtype: dict
        """
        options = super(CommandlineToAny, self).fix_config(options)

        opt = "wrapper"
        if opt not in options:
            options[opt] = "weka.core.classes.OptionHandler"
        if opt not in self.help:
            self.help[opt] = "The name of the wrapper class to use (string)."

        return options

    def check_input(self, obj):
        """
        Performs checks on the input object. Raises an exception if unsupported.

        :param obj: the object to check
        :type obj: object
        """
        if isinstance(obj, str):
            return
        if isinstance(obj, unicode):
            return
        raise Exception("Unsupported class: " + self._input.__class__.__name__)

    def convert(self):
        """
        Performs the actual conversion.

        :return: None if successful, otherwise errors message
        :rtype: str
        """
        cname = str(self.config["wrapper"])
        self._output = classes.from_commandline(self._input, classname=cname)
        return None
