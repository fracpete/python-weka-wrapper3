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

# __init__.py
# Copyright (C) 2014-2022 Fracpete (pythonwekawrapper at gmail dot com)

from weka.core.dataset import Instances
from weka.core.classes import Random
from packaging import version

# check whether pygraphviz is there
pygraphviz_available = False
try:
    import pygraphviz
    pygraphviz_available = True
except ImportError:
    pass

# check whether PIL is there
PIL_available = False
try:
    import PIL
    PIL_available = True
except ImportError:
    pass

# check whether matplotlib is there
matplotlib_available = False
matplotlib_version = None
try:
    import matplotlib
    matplotlib_available = True
    matplotlib_version = matplotlib.__version__
except ImportError:
    pass

# check whether lxml is there
lxml_available = False
try:
    from lxml import etree
    lxml_available = True
except ImportError:
    pass


def create_subsample(data, percent, seed=1):
    """
    Generates a subsample of the dataset.
    :param data: the data to create the subsample from
    :type data: Instances
    :param percent: the percentage (0-100)
    :type percent: float
    :param seed: the seed value to use
    :type seed: int
    """
    if percent <= 0 or percent >= 100:
        return data
    data = Instances.copy_instances(data)
    data.randomize(Random(seed))
    data = Instances.copy_instances(data, 0, int(round(data.num_instances * percent / 100.0)))
    return data


def set_window_title(fig, title):
    """
    Sets the window title of the figure (if matplotlib is available).

    :param fig: the figure to update
    :param title: the title to set
    :type title: str
    """
    if matplotlib_available:
        if version.parse(matplotlib_version) >= version.parse("3.4.0"):
            fig.canvas.manager.set_window_title(title)
        else:
            fig.canvas.set_window_title(title)
