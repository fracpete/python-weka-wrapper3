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

# systeminfo.py
# Copyright (C) 2020 Fracpete (pythonwekawrapper at gmail dot com)

from weka.core.classes import JavaObject
import javabridge


def system_info():
    """
    Returns a dictionary generated from the output of weka.core.SystemInfo.

    :return: the system info as dictionary
    :rtype: dict
    """
    jobj = JavaObject.new_instance("weka.core.SystemInfo")
    info = javabridge.call(jobj, "getSystemInfo", "()Ljava/util/Hashtable;")
    return javabridge.jdictionary_to_string_dictionary(info)
