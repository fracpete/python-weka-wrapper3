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
# Copyright (C) 2020-2024 Fracpete (pythonwekawrapper at gmail dot com)

from jpype import JClass


def system_info():
    """
    Returns a dictionary generated from the output of weka.core.SystemInfo.

    :return: the system info as dictionary
    :rtype: dict
    """
    result = dict()
    info = JClass("weka.core.SystemInfo")().getSystemInfo()
    for k in info.keys():
        result[k] = info[k]
    return result
