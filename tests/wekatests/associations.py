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

# associations.py
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.converters as converters
import weka.associations as associations
import wekatests.tests.weka_test as weka_test


class TestAssociations(weka_test.WekaTest):

    def test_instantiate_associator(self):
        """
        Tests the instantiation of an Associator class.
        """
        cname = "weka.associations.Apriori"
        options = None
        cls = associations.Associator(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, cls.classname, "Classnames differ!")

    def test_make_copy(self):
        """
        Tests the make_copy class method of the Associator class.
        """
        cname = "weka.associations.Apriori"
        options = None
        cls = associations.Associator(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, cls.classname, "Classnames differ!")
        cls2 = associations.Associator.make_copy(cls)
        self.assertIsNotNone(cls2, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, cls2.classname, "Classnames differ!")

    def test_capabilities(self):
        """
        Tests the capabilities.
        """
        cname = "weka.associations.Apriori"
        options = None
        cls = associations.Associator(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))
        self.assertEqual(cname, cls.classname, "Classnames differ!")

        caps = cls.capabilities
        self.assertIsNotNone(caps, msg="Capabilities are None!")

    def test_build_associator(self):
        """
        Tests the build_classifier method.
        """
        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("nursery.arff"))
        self.assertIsNotNone(data)
        data.class_is_last()

        cname = "weka.associations.Apriori"
        options = None
        cls = associations.Associator(classname=cname, options=options)
        self.assertIsNotNone(cls, msg="Failed to instantiate: " + cname + "/" + str(options))

        cls.build_associations(data)


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestAssociations)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
