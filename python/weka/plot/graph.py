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

# graph.py
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import logging
import tempfile
import weka.plot as plot
if plot.pygraphviz_available:
    from pygraphviz.agraph import AGraph
if plot.PIL_available:
    from PIL import Image

# logging setup
logger = logging.getLogger(__name__)


def plot_dot_graph(graph, filename=None):
    """
    Plots a graph in graphviz dot notation.

    :param graph: the dot notation graph
    :type graph: str
    :param filename: the (optional) file to save the generated plot to. The extension determines the file format.
    :type filename: str
    """
    if not plot.pygraphviz_available:
        logger.error("Pygraphviz is not installed, cannot generate graph plot!")
        return
    if not plot.PIL_available:
        logger.error("PIL is not installed, cannot display graph plot!")
        return

    agraph = AGraph(graph)
    agraph.layout(prog='dot')
    if filename is None:
        filename = tempfile.mktemp(suffix=".png")
    agraph.draw(filename)
    image = Image.open(filename)
    image.show()
