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

# experiments.py
# Copyright (C) 2015-2023 Fracpete (pythonwekawrapper at gmail dot com)

import logging
import math
import weka.plot as plot
if plot.matplotlib_available:
    import matplotlib.pyplot as plt
from weka.experiments import ResultMatrix

# logging setup
logger = logging.getLogger(__name__)


def plot_experiment(mat, title="Experiment", axes_swapped=False, measure="Statistic", show_stdev=False,
                    x_label=None, y_label=None, key_loc="lower right", bbox_to_anchor=None, outfile=None, wait=True):
    """
    Plots the results from an experiment.

    :param mat: the result matrix to plot
    :type mat: ResultMatrix
    :param title: the title for the experiment
    :type title: str
    :param axes_swapped: whether the axes whether swapped for the evaluation ("datasets x classifers" or "classifers x datasets")
    :type axes_swapped: bool
    :param measure: the measure that is being displayed
    :type measure: str
    :param show_stdev: whether to show the standard deviation as error bar
    :type show_stdev: bool
    :param x_label: the label to override the default x label with (ie Classifiers/Datasets)
    :type x_label: str
    :param y_label: the label to override the default y label with (ie the measure)
    :type y_label: str
    :param key_loc: the location string for the key
    :type key_loc: str
    :param bbox_to_anchor: tuple for the key anchor
    :type bbox_to_anchor: tuple
    :param outfile: the output file, ignored if None
    :type outfile: str
    :param wait: whether to wait for the user to close the plot
    :type wait: bool
    """

    if not plot.matplotlib_available:
        logger.error("Matplotlib is not installed, plotting unavailable!")
        return

    if not isinstance(mat, ResultMatrix):
        logger.error("Need to supply a result matrix!")
        return

    fig, ax = plt.subplots()
    if axes_swapped:
        ax.set_xlabel(x_label if x_label is not None else "Datasets")
        ax.set_ylabel(y_label if y_label is not None else measure)
    else:
        ax.set_xlabel(x_label if x_label is not None else "Classifiers")
        ax.set_ylabel(y_label if y_label is not None else measure)
    ax.set_title(title)
    plot.set_window_title(fig, title)
    ax.grid(True)
    ticksx = []
    ticks = []
    inc = 1.0 / float(mat.columns)
    for i in range(mat.columns):
        ticksx.append((i + 0.5) * inc)
        ticks.append("[" + str(i+1) + "]")
    plt.xticks(ticksx, ticks)
    plt.xlim([0.0, 1.0])
    for r in range(mat.rows):
        x = []
        means = []
        stdevs = []
        for c in range(mat.columns):
            mean = mat.get_mean(c, r)
            stdev = mat.get_stdev(c, r)
            if not math.isnan(mean):
                x.append((c + 0.5) * inc)
                means.append(mean)
                if not math.isnan(stdev):
                    stdevs.append(stdev)
        plot_label = mat.get_row_name(r)
        if show_stdev:
            ax.errorbar(x, means, yerr=stdevs, fmt='-o', label=plot_label)
        else:
            ax.plot(x, means, "o-", label=plot_label)
    plt.draw()
    plt.legend(loc=key_loc, bbox_to_anchor=bbox_to_anchor, mode="expand", shadow=True)
    if outfile is not None:
        plt.savefig(outfile)
    if wait:
        plt.show()
