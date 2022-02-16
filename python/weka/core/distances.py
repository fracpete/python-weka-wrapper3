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
# Copyright (C) 2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
from weka.core.classes import OptionHandler
from weka.core.dataset import Instances, Instance


class DistanceFunction(OptionHandler):
    """
    Wrapper for Weka's weka.core.DistanceFunction interface.
    """

    def __init__(self, classname="weka.core.EuclideanDistance", jobject=None, options=None):
        """
        Initializes the specified distance function using either the classname or the supplied JB_Object.

        :param classname: the classname of the distance function
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = DistanceFunction.new_instance(classname)
        self.enforce_type(jobject, "weka.core.DistanceFunction")
        super(DistanceFunction, self).__init__(jobject=jobject, options=options)

    def _make_calls(self):
        """
        Method for generating instances using javabridge.make_call.
        Members must start with "_mc_"
        """
        super(DistanceFunction, self)._make_calls()
        self._distance = javabridge.make_call(self.jobject, "distance", "(Lweka/core/Instance;Lweka/core/Instance;)D")
        self._distance_cutoff = javabridge.make_call(self.jobject, "distance", "(Lweka/core/Instance;Lweka/core/Instance;D)D")

    @property
    def instances(self):
        """
        Returns the dataset in use.

        :return: the dataset
        :rtype: Instances
        """
        inst = javabridge.call(self.jobject, "getInstances", "()Lweka/core/Instances;")
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
        javabridge.call(self.jobject, "setInstances", "(Lweka/core/Instances;)V", instances.jobject)

    @property
    def attribute_indices(self):
        """
        Returns the attribute indices in use.

        :return: the attribute indices
        :rtype: str
        """
        return javabridge.call(self.jobject, "getAttributeIndices", "()Ljava/lang/String;")

    @attribute_indices.setter
    def attribute_indices(self, indices):
        """
        Sets the attribute indices to use.

        :param indices: the indices to use
        :type indices: str
        """
        javabridge.call(self.jobject, "setAttributeIndices", "(Ljava/lang/String;)V", indices)
    
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
