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

# serialization.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

# for backwards compatibility
from weka.core.classes import deepcopy
from weka.core.classes import serialization_read as read
from weka.core.classes import serialization_read_all as read_all
from weka.core.classes import serialization_write as write
from weka.core.classes import serialization_write_all as write_all
from weka.core.classes import to_byte_array
from weka.core.classes import from_byte_array
