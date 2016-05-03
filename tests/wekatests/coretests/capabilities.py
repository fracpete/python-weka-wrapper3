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
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.capabilities as capabilities
import weka.classifiers as classifiers
import wekatests.tests.weka_test as weka_test


class TestCapabilities(weka_test.WekaTest):

    def test_capability(self):
        """
        Tests the Capability class.
        """
        member = "NOMINAL_ATTRIBUTES"
        cap = capabilities.Capability(member=member)
        self.assertIsNotNone(cap, msg="Failed to instantiate capability: " + member)
        self.assertEqual(member, cap.name, "Names differ")
        self.assertTrue(cap.is_attribute)
        self.assertTrue(cap.is_attribute_capability)
        self.assertFalse(cap.is_class)
        self.assertFalse(cap.is_class_capability)
        self.assertFalse(cap.is_other_capability)

    def test_capabilities(self):
        """Tests the Capabilities class.
        """
        caps = capabilities.Capabilities()
        self.assertIsNotNone(caps, msg="Failed to instantiate empty capabilities")
        self.assertEqual(0, len(caps.capabilities()), msg="Should have no capabilities")

        cls = classifiers.Classifier(classname="weka.classifiers.trees.J48")
        caps = capabilities.Capabilities(owner=cls)
        self.assertIsNotNone(caps, msg="Failed to instantiate empty capabilities")
        self.assertEqual(0, len(caps.capabilities()), msg="Should have no capabilities")
        self.assertIsNotNone(caps.owner, msg="Should have an owner")
        caps.owner = None
        self.assertIsNone(caps.owner, msg="Should have no owner")
        caps.owner = cls
        self.assertIsNotNone(caps.owner, msg="Should have an owner")

        cap = capabilities.Capability(member="NUMERIC_CLASS")
        caps.enable(cap)
        self.assertTrue(caps.handles(cap), "Should have capability: " + str(cap))
        self.assertFalse(caps.has_dependency(cap), "Should have no dependency: " + str(cap))
        self.assertEqual(0, len(caps.dependencies()), msg="Should have no dependencies")
        caps.enable_dependency(cap)
        self.assertTrue(caps.has_dependency(cap), "Should have dependency: " + str(cap))
        self.assertEqual(1, len(caps.dependencies()), msg="Should have one dependency")

        caps.disable_all()
        self.assertEqual(0, len(caps.capabilities()), msg="Should have no capabilities")
        self.assertEqual(0, len(caps.dependencies()), msg="Should have no dependencies")

        caps.enable_all()
        self.assertGreater(len(caps.capabilities()), 0, msg="Should have capabilities")
        self.assertGreater(len(caps.dependencies()), 0, msg="Should have dependencies")

        caps.disable_all()
        caps.enable_all_attribute_dependencies()
        self.assertEqual(0, len(caps.capabilities()), msg="Should have no capabilities")
        self.assertGreater(len(caps.dependencies()), 0, msg="Should have dependencies")

        caps.disable_all()
        caps.enable_all_attributes()
        self.assertGreater(len(caps.capabilities()), 0, msg="Should have capabilities")
        self.assertEqual(0, len(caps.dependencies()), msg="Should have no dependencies")

        caps.disable_all()
        caps.enable_all_class_dependencies()
        self.assertEqual(0, len(caps.capabilities()), msg="Should have no capabilities")
        self.assertGreater(len(caps.dependencies()), 0, msg="Should have dependencies")

        caps.disable_all()
        caps.enable_all_classes()
        self.assertGreater(len(caps.capabilities()), 0, msg="Should have capabilities")
        self.assertEqual(0, len(caps.dependencies()), msg="Should have no dependencies")


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestCapabilities)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
