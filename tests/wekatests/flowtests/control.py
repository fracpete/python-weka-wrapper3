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

# control.py
# Copyright (C) 2015-2016 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import os
import weka.core.jvm as jvm
import weka.classifiers as classifiers
import weka.flow.control as control
import weka.flow.source as source
import weka.flow.transformer as transformer
import weka.flow.sink as sink
import wekatests.tests.weka_test as weka_test


class TestControl(weka_test.WekaTest):

    def test_instantiation(self):
        """
        Tests instantiating of control actors.
        """
        actor = control.Flow()
        self.assertIsNotNone(actor, msg="Actor should not be None")

    def test_shallow_copy(self):
        """
        Tests the shallow_copy method.
        """
        actor = control.Flow()
        actor.name = "blah"
        actor.config["annotation"] = "Some annotation text"
        actor2 = actor.shallow_copy()
        self.assertEqual(actor.name, actor2.name, msg="Names differ")
        self.assertEqual(actor.config, actor2.config, msg="Configs differ")

    def test_json(self):
        """
        Tests the json methods.
        """
        actor = control.Flow()
        actor.name = "blah"
        actor.config["annotation"] = "Some annotation text"
        actor.actors.append(source.Start())
        tee = control.Tee()
        actor.actors.append(tee)
        tee.actors.append(sink.Console())
        trigger = control.Trigger()
        actor.actors.append(trigger)
        files = source.FileSupplier()
        files.config["files"] = ["file1.arff", "file2.arff"]
        trigger.actors.append(files)
        loader = transformer.LoadDataset()
        trigger.actors.append(loader)
        select = transformer.ClassSelector()
        trigger.actors.append(select)
        train = transformer.Train()
        train.config["setup"] = classifiers.Classifier(classname="weka.classifiers.trees.J48", options=["-C", "0.3"])
        trigger.actors.append(train)
        json = actor.to_json()
        flow2 = control.Flow.from_json(json)
        json2 = flow2.to_json()
        self.assertEqual(json, json2, msg="JSON representations differ")


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestControl)


if __name__ == '__main__':
    jvm.start()
    unittest.TextTestRunner().run(suite())
    jvm.stop()
