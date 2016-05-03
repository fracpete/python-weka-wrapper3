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

# container.py
# Copyright (C) 2015-2016 Fracpete (pythonwekawrapper at gmail dot com)

import re
from weka.core.dataset import Instances


class Container(object):
    """
    Container for storing multiple objects and passing them around together in the flow.
    """

    def __init__(self):
        """
        Initializes the container.
        """
        self._data = {}
        self._allowed = []

    def get(self, name):
        """
        Returns the stored data.

        :param name: the name of the item to return
        :type name: str
        :return: the data
        :rtype: object
        """
        return self._data[name]

    def set(self, name, value):
        """
        Stores the given data (if not None).

        :param name: the name of the item to store
        :type name: str
        :param value: the value to store
        :type value: object
        """
        if value is not None:
            self._data[name] = value

    @property
    def allowed(self):
        """
        Returns the all the allowed keys.

        :return: the list of allowed keys.
        :rtype: list
        """
        return self._allowed

    def is_valid(self):
        """
        Checks whether the container is valid.

        :return: True if the container is valid
        :rtype: bool
        """
        return True

    def __str__(self):
        """
        Returns the content of the container as string.

        :return: the content
        :rtype: str
        """
        return str(self._data)

    def generate_help(self):
        """
        Generates a help string for this container.

        :return: the help string
        :rtype: str
        """
        result = []
        result.append(self.__class__.__name__)
        result.append(re.sub(r'.', '=', self.__class__.__name__))
        result.append("")
        result.append("Supported value names:")
        for a in self.allowed:
            result.append(a)
        return '\n'.join(result)

    def print_help(self):
        """
        Prints a help string for this actor to stdout.
        """
        print(self.generate_help())


class ModelContainer(Container):
    """
    Container for models.
    """

    def __init__(self, model=None, header=None):
        """
        Initializes the container.

        :param model: the model to store (eg Classifier or Clusterer)
        :type model: object
        :param header: the header instances
        :type header: Instances
        """
        super(ModelContainer, self).__init__()
        self.set("Model", model)
        if header is not None:
            header = Instances.template_instances(header)
        self.set("Header", header)
        self._allowed = ["Model", "Header"]

    def is_valid(self):
        """
        Checks whether the container is valid.

        :return: True if the container is valid
        :rtype: bool
        """
        return ("Model" in self._data) or ("Model" in self._data and "Header" in self._data)


class AttributeSelectionContainer(Container):
    """
    Container for models.
    """

    def __init__(self, original=None, reduced=None, num_atts=None, selected=None, results=None):
        """
        Initializes the container.

        :param original: the original dataset
        :type original: Instances
        :param reduced: the reduced dataset
        :type reduced: Instances
        :param num_atts: the number of attributes
        :type num_atts: int
        :param selected: the list of selected attribute indices (0-based)
        :type selected: list
        :param results: the generated results string
        :type results: str
        """
        super(AttributeSelectionContainer, self).__init__()
        self.set("Original", original)
        self.set("Reduced", reduced)
        self.set("NumAttributes", num_atts)
        self.set("Selected", selected)
        self.set("Results", results)
        self._allowed = ["Original", "Reduced", "NumAttributes", "Selected", "Results"]

    def is_valid(self):
        """
        Checks whether the container is valid.

        :return: True if the container is valid
        :rtype: bool
        """
        return ("Reduced" in self._data) and ("NumAttributes" in self._data) and ("Selected" in self._data)


class ModelContainer(Container):
    """
    Container for models.
    """

    def __init__(self, model=None, header=None):
        """
        Initializes the container.

        :param model: the model to store (eg Classifier or Clusterer)
        :type model: object
        :param header: the header instances
        :type header: Instances
        """
        super(ModelContainer, self).__init__()
        self.set("Model", model)
        if header is not None:
            header = Instances.template_instances(header)
        self.set("Header", header)
        self._allowed = ["Model", "Header"]

    def is_valid(self):
        """
        Checks whether the container is valid.

        :return: True if the container is valid
        :rtype: bool
        """
        return ("Model" in self._data) or ("Model" in self._data and "Header" in self._data)


class ClassificationContainer(Container):
    """
    Container for predictions (classifiers).
    """

    def __init__(self, inst=None, classification=None, label=None, distribution=None):
        """
        Initializes the container.

        :param inst: the instance used for making the prediction
        :type inst: Instance
        :param classification: the classification (numeric value or 0-based label index)
        :type classification: float
        :param label: classification label (for nominal classes)
        :type label: str
        :param distribution: the class distribution
        :type distribution: ndarray
        """
        super(ClassificationContainer, self).__init__()
        self.set("Instance", inst)
        self.set("Classification", classification)
        self.set("Label", label)
        self.set("Distribution", distribution)
        self._allowed = ["Instance", "Classification", "Label", "Distribution"]

    def is_valid(self):
        """
        Checks whether the container is valid.

        :return: True if the container is valid
        :rtype: bool
        """
        return ("Instance" in self._data) and ("Classification" in self._data)


class ClusteringContainer(Container):
    """
    Container for predictions (clusterers).
    """

    def __init__(self, inst=None, cluster=None, distribution=None):
        """
        Initializes the container.

        :param inst: the instance used for making the prediction
        :type inst: Instance
        :param cluster: the cluster
        :type cluster: int
        :param distribution: the class distribution
        :type distribution: ndarray
        """
        super(ClusteringContainer, self).__init__()
        self.set("Instance", inst)
        self.set("Cluster", cluster)
        self.set("Distribution", distribution)
        self._allowed = ["Instance", "Cluster", "Distribution"]

    def is_valid(self):
        """
        Checks whether the container is valid.

        :return: True if the container is valid
        :rtype: bool
        """
        return ("Instance" in self._data) and ("Cluster" in self._data)
