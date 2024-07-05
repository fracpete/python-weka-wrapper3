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

# capabilities.py
# Copyright (C) 2014-2024 Fracpete (pythonwekawrapper at gmail dot com)

from jpype import JClass
from weka.core.classes import JavaObject, Enum
from weka.core.dataset import Attribute, Instances


class Capability(Enum):
    """
    Wrapper for a Capability.
    """

    def __init__(self, jobject=None, member=None):
        """
        Initializes the wrapper with the specified Capability object.

        :param jobject: the Capability object to wrap
        :type jobject: JPype object
        :param member: the capability string to parse
        :type member: str
        """
        super(Capability, self).__init__(jobject=jobject, enum="weka.core.Capabilities$Capability", member=member)

    @property
    def is_attribute(self):
        """
        Returns whether this capability is an attribute.

        :return: whether it is an attribute
        :rtype: bool
        """
        return self.jobject.isAttribute()

    @property
    def is_attribute_capability(self):
        """
        Returns whether this capability is an attribute capability.

        :return: whether it is an attribute capability
        :rtype: bool
        """
        return self.jobject.isAttributeCapability()

    @property
    def is_class(self):
        """
        Returns whether this capability is a class.

        :return: whether it is a class
        :rtype: bool
        """
        return self.jobject.isClass()

    @property
    def is_class_capability(self):
        """
        Returns whether this capability is a class capability.

        :return: whether it is a class capability
        :rtype: bool
        """
        return self.jobject.isClassCapability()

    @property
    def is_other_capability(self):
        """
        Returns whether this capability is an other capability.

        :return: whether it is an other capability
        :rtype: bool
        """
        return self.jobject.isOtherCapability()


class Capabilities(JavaObject):
    """
    Wrapper for Capabilities.
    """

    def __init__(self, jobject=None, owner=None):
        """
        Initializes the wrapper with the specified Capabilities object.

        :param jobject: the Capabilities object to wrap, instantiates a new one if None
        :type jobject: JPype object
        :param owner: the weka.core.CapabilitiesHandler object to use as owner, can be None
        :type owner: JPype object or JavaObject
        """
        if jobject is None:
            if isinstance(owner, JavaObject):
                owner = owner.jobject
            jobject = JClass("weka.core.Capabilities")(owner)
        Capabilities.enforce_type(jobject, "weka.core.Capabilities")
        super(Capabilities, self).__init__(jobject)

    @property
    def owner(self):
        """
        Returns the owner of these capabilities, if any.

        :return: the owner, can be None
        :rtype: JavaObject
        """
        obj = self.jobject.getOwner()
        if obj is None:
            return None
        else:
            return JavaObject(jobject=obj)

    @owner.setter
    def owner(self, obj):
        """
        Sets the new owner.

        :param obj: the new owner
        :type obj: JavaObject or JPype object
        """
        if isinstance(obj, JavaObject):
            obj = obj.jobject
        self.jobject.setOwner(obj)

    def capabilities(self):
        """
        Returns all the capabilities.

        :return: all capabilities
        :rtype: list
        """
        result = []
        for c in self.jobject.capabilities():
            result.append(Capability(c))
        return result

    def attribute_capabilities(self):
        """
        Returns all the attribute capabilities.

        :return: attribute capabilities
        :rtype: Capabilities
        """
        return Capabilities(
            self.jobject.getAttributeCapabilities())

    def class_capabilities(self):
        """
        Returns all the class capabilities.

        :return: class capabilities
        :rtype: Capabilities
        """
        return Capabilities(
            self.jobject.getClassCapabilities())

    def other_capabilities(self):
        """
        Returns all other capabilities.

        :return: all other capabilities
        :rtype: Capabilities
        """
        return Capabilities(
            self.jobject.getOtherCapabilities())

    def dependencies(self):
        """
        Returns all the dependencies.

        :return: the dependency list
        :rtype: list
        """
        result = []
        for c in self.jobject.dependencies():
            result.append(Capability(c))
        return result

    def handles(self, capability):
        """
        Returns whether the specified capability is set.

        :param capability: the capability to check
        :type capability: Capability
        :return: whether the capability is set
        :rtype: bool
        """
        return self.jobject.handles(capability.jobject)

    def enable_all(self):
        """
        enables all capabilities.
        """
        self.jobject.enableAll()

    def enable_all_attributes(self):
        """
        enables all attributes.
        """
        self.jobject.enableAllAttributes()

    def enable_all_classes(self):
        """
        enables all classes.
        """
        self.jobject.enableAllClasses()

    def enable(self, capability):
        """
        enables the specified capability.

        :param capability: the capability to enable
        :type capability: Capability
        """
        self.jobject.enable(capability.jobject)

    def enable_all_attribute_dependencies(self):
        """
        enables all attribute dependencies.
        """
        self.jobject.enableAllAttributeDependencies()

    def enable_all_class_dependencies(self):
        """
        enables all class dependencies.
        """
        self.jobject.enableAllClassDependencies()

    def enable_dependency(self, capability):
        """
        enables the dependency of the given capability enabling NOMINAL_ATTRIBUTES also enables
        BINARY_ATTRIBUTES, UNARY_ATTRIBUTES and EMPTY_NOMINAL_ATTRIBUTES.

        :param capability: the dependency to enable
        :type capability: Capability
        """
        self.jobject.enableDependency(capability.jobject)

    def disable_all(self):
        """
        Disables all capabilities.
        """
        self.jobject.disableAll()

    def disable_all_attributes(self):
        """
        Disables all attributes.
        """
        self.jobject.disableAllAttributes()

    def disable_all_classes(self):
        """
        Disables all classes.
        """
        self.jobject.disableAllClasses()

    def disable(self, capability):
        """
        Disables the specified capability.

        :param capability: the capability to disable
        :type capability: Capability
        """
        self.jobject.disable(capability.jobject)

    def disable_all_attribute_dependencies(self):
        """
        Disables all attribute dependencies.
        """
        self.jobject.disableAllAttributeDependencies()

    def disable_all_class_dependencies(self):
        """
        Disables all class dependencies.
        """
        self.jobject.disableAllClassDependencies()

    def disable_dependency(self, capability):
        """
        Disables the dependency of the given capability Disabling NOMINAL_ATTRIBUTES also disables
        BINARY_ATTRIBUTES, UNARY_ATTRIBUTES and EMPTY_NOMINAL_ATTRIBUTES.

        :param capability: the dependency to disable
        :type capability: Capability
        """
        self.jobject.disableDependency(capability.jobject)

    def has_dependencies(self):
        """
        Returns whether any dependencies are set.

        :return: whether any dependecies are set
        :rtype: bool
        """
        return self.jobject.hasDependencies()

    def has_dependency(self, capability):
        """
        Returns whether the specified dependency is set.

        :param capability: the capability to check
        :type capability: Capability
        :return: whether the dependency is set
        :rtype: bool
        """
        return self.jobject.hasDependency(capability.jobject)

    def supports(self, capabilities):
        """
        Returns true if the currently set capabilities support at least all of the capabiliites of the given
        Capabilities object (checks only the enum!)

        :param capabilities: the capabilities to check
        :type capabilities: Capabilities
        :return: whether the current capabilities support at least the specified ones
        :rtype: bool
        """
        return self.jobject.supports(capabilities.jobject)

    def supports_maybe(self, capabilities):
        """
        Returns true if the currently set capabilities support (or have a dependency) at least all of the
        capabilities of the given Capabilities object (checks only the enum!)

        :param capabilities: the capabilities to check
        :type capabilities: Capabilities
        :return: whether the current capabilities (potentially) support the specified ones
        :rtype: bool
        """
        return self.jobject.supportsMaybe(capabilities.jobject)

    @property
    def min_instances(self):
        """
        Returns the minimum number of instances that must be supported.

        :return: the minimum number
        :rtype: int
        """
        return self.jobject.getMinimumNumberInstances()

    @min_instances.setter
    def min_instances(self, minimum):
        """
        Sets the minimum number of instances that must be supported.

        :param minimum: the minimum number
        :type minimum: int
        """
        self.jobject.setMinimumNumberInstances(minimum)

    def test_attribute(self, att, is_class=None, fail=False):
        """
        Tests whether the attribute meets the conditions.

        :param att: the Attribute to test
        :type att: Attribute
        :param is_class: whether this attribute is the class attribute
        :type is_class: bool
        :param fail: whether to fail with an exception in case the test fails
        :type fail: bool
        :return: whether the attribute meets the conditions
        :rtype: bool
        """
        if fail:
            if is_class is None:
                return self.jobject.test(att.jobject)
            else:
                return self.jobject.test(att.jobject, is_class)
        else:
            if is_class is None:
                return self.jobject.testWithFail(att.jobject)
            else:
                return self.jobject.testWithFail(att.jobject, is_class)

    def test_instances(self, data, from_index=None, to_index=None, fail=False):
        """
        Tests whether the dataset meets the conditions.

        :param data: the Instances to test
        :type data: Instances
        :param from_index: the first attribute to include
        :type from_index: int
        :param to_index: the last attribute to include
        :type to_index: int
        :return: wether the dataset meets the requirements
        :rtype: bool
        """
        if fail:
            if (from_index is None) or (to_index is None):
                return self.jobject.test(data.jobject)
            else:
                return self.jobject.test(data.jobject, from_index, to_index)
        else:
            if (from_index is None) or (to_index is None):
                return self.jobject.testWithFail(data.jobject)
            else:
                return self.jobject.testWithFail(data.jobject, from_index, to_index)

    @classmethod
    def for_instances(cls, data, multi=None):
        """
        returns a Capabilities object specific for this data. The minimum number of instances is not set, the check
        for multi-instance data is optional.

        :param data: the data to generate the capabilities for
        :type data: Instances
        :param multi: whether to check the structure, too
        :type multi: bool
        :return: the generated capabilities
        :rtype: Capabilities
        """
        if multi is None:
            return Capabilities(JClass("weka.core.Capabilities").forInstances(data.jobject))
        else:
            return Capabilities(JClass("weka.core.Capabilities").forInstances(data.jobject, multi))
