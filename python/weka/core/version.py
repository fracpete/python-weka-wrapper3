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

# version.py
# Copyright (C) 2014-2018 Fracpete (pythonwekawrapper at gmail dot com)

from weka.core.classes import JavaObject


def weka_version():
    """
    Determines the version of Weka in use.

    :return: the version
    :rtype: str
    """
    jobj = JavaObject(JavaObject.new_instance("weka.core.Version"))
    return str(jobj)
