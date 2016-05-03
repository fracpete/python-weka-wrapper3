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

# weka_test.py
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import tempfile
import os


class WekaTest(unittest.TestCase):
    """
    Weka-specific test case class.
    """

    def tempdir(self):
        """
        Returns the temp directory.
        :return: the temp directory
        :rtype: str
        """
        return tempfile.gettempdir()

    def tempfile(self, fname):
        """
        Generates a full path for the given filename (without path) and returns it.
        :param fname: the filename (without path)
        :type fname: str
        :return: the full path
        :rtype: str
        """
        return self.tempdir() + os.sep + fname

    def delfile(self, path):
        """
        Removes the file from the file system.
        :param path: the full path to the file
        :type path: str
        :return: whether successfully removed (also True if not present)
        :rtype: bool
        """
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except Exception as e:
                print("Failed to remove: " + path + "\n" + str(e))
                return False
        else:
            return True

    def datadir(self):
        """
        Returns the data directory.
        :return: the data directory
        :rtype: str
        """
        rootdir = os.path.dirname(__file__)
        libdir = rootdir + os.sep + ".." + os.sep + "data"
        return libdir

    def datafile(self, fname):
        """
        Returns the full path for the file (without path) and returns it.
        :param fname: the filename (without path)
        :type fname: str
        :return: the full path
        :rtype: str
        """
        return self.datadir() + os.sep + fname
