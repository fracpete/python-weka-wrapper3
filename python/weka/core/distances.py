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

# distances.py
# Copyright (C) 2021-2024 Fracpete (pythonwekawrapper at gmail dot com)

from weka.core.classes import OptionHandler
from weka.core.dataset import Instances, Instance


class DistanceFunction(OptionHandler):
    """
    Wrapper for Weka's weka.core.DistanceFunction interface.
    """

    def __init__(self, classname="weka.core.EuclideanDistance", jobject=None, options=None):
        """
        Initializes the specified distance function using either the classname or the supplied JPype object.

        :param classname: the classname of the distance function
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: the list of commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = DistanceFunction.new_instance(classname)
        self.enforce_type(jobject, "weka.core.DistanceFunction")
        super(DistanceFunction, self).__init__(jobject=jobject, options=options)

    def _make_calls(self):
        """
        Method for obtaining method instances for faster access.
        Members must start with "_mc_"
        """
        super(DistanceFunction, self)._make_calls()
        self._distance = self.jobject.distance

    @property
    def instances(self):
        """
        Returns the dataset in use.

        :return: the dataset
        :rtype: Instances
        """
        inst = self.jobject.getInstances()
        if inst is None:
            return None
        else:
            return Instances(jobject=inst)

    @instances.setter
    def instances(self, instances):
        """
        Sets the dataset to use.

        :param instances: the dataset to use
        :type instances: Instances
        """
        self.jobject.setInstances(instances.jobject)

    @property
    def attribute_indices(self):
        """
        Returns the attribute indices in use.

        :return: the attribute indices
        :rtype: str
        """
        return self.jobject.getAttributeIndices()

    @attribute_indices.setter
    def attribute_indices(self, indices):
        """
        Sets the attribute indices to use.

        :param indices: the indices to use
        :type indices: str
        """
        self.jobject.setAttributeIndices(indices)
    
    def distance(self, first, second, cutoff=None):
        """
        Computes the distance between the two Instance objects.

        :param first: the first instance
        :type first: Instance
        :param second: the second instance
        :type second: Instance
        :param cutoff: optional cutoff value to speed up calculation
        :type cutoff: float
        :return: the calculated distance
        :rtype: float
        """
        if cutoff is None:
            return self._distance(first.jobject, second.jobject)
        else:
            return self._distance(first.jobject, second.jobject, cutoff)
