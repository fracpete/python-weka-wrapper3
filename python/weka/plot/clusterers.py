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

# clusterers.py
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import logging
import weka.plot as plot
if plot.matplotlib_available:
    import matplotlib.pyplot as plt
from weka.core.dataset import Instances
from weka.clusterers import ClusterEvaluation

# logging setup
logger = logging.getLogger(__name__)


def plot_cluster_assignments(evl, data, atts=None, inst_no=False, size=10, title=None, outfile=None, wait=True):
    """
    Plots the cluster assignments against the specified attributes.

    TODO: click events http://matplotlib.org/examples/event_handling/data_browser.html

    :param evl: the cluster evaluation to obtain the cluster assignments from
    :type evl: ClusterEvaluation
    :param data: the dataset the clusterer was evaluated against
    :type data: Instances
    :param atts: the list of attribute indices to plot, None for all
    :type atts: list
    :param inst_no: whether to include a fake attribute with the instance number
    :type inst_no: bool
    :param size: the size of the circles in point
    :type size: int
    :param title: an optional title
    :type title: str
    :param outfile: the (optional) file to save the generated plot to. The extension determines the file format.
    :type outfile: str
    :param wait: whether to wait for the user to close the plot
    :type wait: bool
    """
    if not plot.matplotlib_available:
        logger.error("Matplotlib is not installed, plotting unavailable!")
        return

    fig = plt.figure()

    if data.class_index == -1:
        c = None
    else:
        c = []
        for i in range(data.num_instances):
            inst = data.get_instance(i)
            c.append(inst.get_value(inst.class_index))

    if atts is None:
        atts = []
        for i in range(data.num_attributes):
            atts.append(i)

    num_plots = len(atts)
    if inst_no:
        num_plots += 1

    clusters = evl.cluster_assignments

    for index, att in enumerate(atts):
        x = data.values(att)
        ax = fig.add_subplot(
            1, num_plots, index + 1)
        if c is None:
            ax.scatter(clusters, x, s=size, alpha=0.5)
        else:
            ax.scatter(clusters, x, c=c, s=size, alpha=0.5)
        ax.set_xlabel("Clusters")
        ax.set_title(data.attribute(att).name)
        ax.get_xaxis().set_ticks(list(set(clusters)))
        ax.grid(True)

    if inst_no:
        x = []
        for i in range(data.num_instances):
            x.append(i+1)
        ax = fig.add_subplot(
            1, num_plots, num_plots)
        if c is None:
            ax.scatter(clusters, x, s=size, alpha=0.5)
        else:
            ax.scatter(clusters, x, c=c, s=size, alpha=0.5)
        ax.set_xlabel("Clusters")
        ax.set_title("Instance number")
        ax.get_xaxis().set_ticks(list(set(clusters)))
        ax.grid(True)

    if title is None:
        title = data.relationname
    fig.canvas.set_window_title(title)
    plt.draw()
    if not outfile is None:
        plt.savefig(outfile)
    if wait:
        plt.show()
