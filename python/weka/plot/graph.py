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
# Copyright (C) 2014-2022 Fracpete (pythonwekawrapper at gmail dot com)

import logging
import tempfile
import weka.plot as plot
if plot.pygraphviz_available:
    from pygraphviz.agraph import AGraph
if plot.PIL_available:
    from PIL import Image
if plot.lxml_available:
    from lxml import etree

# logging setup
logger = logging.getLogger(__name__)


def plot_dot_graph(graph, filename=None):
    """
    Plots a graph in graphviz dot notation.

    http://graphviz.org/doc/info/lang.html

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


def xmlbif_to_dot(graph):
    """
    Converts the graph in XML BIF notation into a dot graph.

    http://sites.poli.usp.br/p/fabio.cozman/Research/InterchangeFormat/index.html

    :param graph: the graph to convert
    :type graph: str
    :return: the graph in dot notation
    :rtype: str
    """
    if not plot.lxml_available:
        logger.error("lxml is not installed, cannot convert XML BIF graph!")
        return

    result = list()
    result.append("digraph {")

    root = etree.fromstring(graph)
    network = root.find("NETWORK")
    definitions = network.findall("DEFINITION")
    for definition in definitions:
        f = definition.find("FOR")
        givens = definition.findall("GIVEN")
        for given in givens:
            result.append("  %s -> %s;" % (given.text, f.text))

    result.append("}")

    return "\n".join(result)


def plot_xmlbif_graph(graph, filename=None):
    """
    Plots a graph in XML BIF notation. Only plots the structure, not the tables.

    http://sites.poli.usp.br/p/fabio.cozman/Research/InterchangeFormat/index.html

    :param graph: the XML BIF notation graph
    :type graph: str
    :param filename: the (optional) file to save the generated plot to. The extension determines the file format.
    :type filename: str
    """
    if not plot.lxml_available:
        logger.error("lxml is not installed, cannot convert XML BIF graph!")
        return
    plot_dot_graph(xmlbif_to_dot(graph), filename)


def plot_graph(graph, filename=None):
    """
    Plots a graph in dot or XML BIF notation.

    http://graphviz.org/doc/info/lang.html
    http://sites.poli.usp.br/p/fabio.cozman/Research/InterchangeFormat/index.html

    :param graph: the dot/XML BIF notation graph
    :type graph: str
    :param filename: the (optional) file to save the generated plot to. The extension determines the file format.
    :type filename: str
    """
    if "<BIF" in graph and "<NETWORK>" in graph:
        return plot_xmlbif_graph(graph, filename=filename)
    else:
        return plot_dot_graph(graph, filename=filename)
