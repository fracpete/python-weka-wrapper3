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

# timeseries.py
# Copyright (C) 2021 Fracpete (pythonwekawrapper at gmail dot com)

import unittest
import weka.core.jvm as jvm
import weka.core.converters as converters
import weka.core.dataset as dataset
import wekatests.tests.weka_test as weka_test
import weka.timeseries as timeseries
import weka.classifiers as classifiers
from weka.core.packages import install_missing_package


class TestTimeseries(weka_test.WekaTest):

    def _ensure_package_is_installed(self):
        install_missing_package("timeseriesForecasting", stop_jvm_and_exit=True)

    def test_instantiate_classes(self):
        """
        Tests the instantiation of several classes.
        """
        self._ensure_package_is_installed()

        obj = timeseries.TSLagMaker()
        cname = "weka.filters.supervised.attribute.TSLagMaker"
        self.assertIsNotNone(obj, msg="Failed to instantiate!")
        self.assertEqual(cname, obj.classname, msg="Classnames differ!")

        obj = timeseries.WekaForecaster()
        cname = "weka.classifiers.timeseries.WekaForecaster"
        self.assertIsNotNone(obj, msg="Failed to instantiate!")
        self.assertEqual(cname, obj.classname, msg="Classnames differ!")

        obj = timeseries.Periodicity("UNKNOWN")
        self.assertIsNotNone(obj, msg="Failed to instantiate!")
        try:
            timeseries.Periodicity("UNKNOWN2")
            self.fail("Unknown enum should have failed!")
        except:
            pass

    def test_evaluate_forecaster(self):
        """
        Tests evaluating a forecaster.
        """
        self._ensure_package_is_installed()

        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("airline.arff"))
        self.assertIsNotNone(data, msg="Data should not be none")
        data.class_is_last()

        forecaster = timeseries.WekaForecaster()
        forecaster.fields_to_forecast = ["passenger_numbers"]
        forecaster.base_forecaster = classifiers.Classifier(classname="weka.classifiers.functions.LinearRegression")
        forecaster.tslag_maker.timestamp_field = "Date"
        forecaster.tslag_maker.adjust_for_variance = False
        forecaster.tslag_maker.include_powers_of_time = True
        forecaster.tslag_maker.include_timelag_products = True
        forecaster.tslag_maker.remove_leading_instances_with_unknown_lag_values = False
        forecaster.tslag_maker.add_month_of_year = True
        forecaster.tslag_maker.add_quarter_of_year = True
        self.assertEqual("LinearRegression -S 0 -R 1.0E-8 -num-decimal-places 4", str(forecaster.algorithm_name), msg="algorithm name")
        self.assertEqual("weka.filters.supervised.attribute.TSLagMaker -F passenger_numbers -L 1 -M 12 -G Date -month -quarter", forecaster.tslag_maker.to_commandline(), msg="lag maker commandline")

        evaluation = timeseries.TSEvaluation(data, 0.0)
        evaluation.evaluate_on_training_data = False
        evaluation.evaluate_on_test_data = False
        evaluation.prime_window_size = forecaster.tslag_maker.max_lag
        evaluation.prime_for_test_data_with_test_data = True
        evaluation.rebuild_model_after_each_test_forecast_step = False
        evaluation.forecast_future = True
        evaluation.horizon = 20
        evaluation.evaluation_modules = "MAE,RMSE"
        evaluation.evaluate(forecaster)

    def test_build_and_use_forecaster(self):
        """
        Tests building and using of a forecaster.
        """
        self._ensure_package_is_installed()

        loader = converters.Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(self.datafile("airline.arff"))
        self.assertIsNotNone(data, msg="Data should not be none")
        data.class_is_last()

        airline_train, airline_test = data.train_test_split(90.0)
        forecaster = timeseries.WekaForecaster()
        self.assertIsNotNone(forecaster)
        forecaster.fields_to_forecast = ["passenger_numbers"]
        forecaster.base_forecaster = classifiers.Classifier(classname="weka.classifiers.functions.LinearRegression")
        forecaster.fields_to_forecast = "passenger_numbers"
        forecaster.build_forecaster(airline_train)
        num_prime_instances = 12
        airline_prime = dataset.Instances.copy_instances(airline_train, airline_train.num_instances - num_prime_instances, num_prime_instances)
        forecaster.prime_forecaster(airline_prime)
        num_future_forecasts = airline_test.num_instances
        preds = forecaster.forecast(num_future_forecasts)
        self.assertIsNotNone(preds, msg="Predictions should not be none")
        self.assertEqual(len(preds), airline_test.num_instances, msg="# of predictions should equal prime window size")


def suite():
    """
    Returns the test suite.
    :return: the test suite
    :rtype: unittest.TestSuite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TestTimeseries)


if __name__ == '__main__':
    jvm.start(packages=True)   # necessary for timeseries package
    unittest.TextTestRunner().run(suite())
    jvm.stop()
