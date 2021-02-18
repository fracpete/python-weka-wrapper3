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

import javabridge
import logging
from weka.core.classes import JavaObject, OptionHandler
from weka.core.dataset import Instances
from weka.classifiers import Classifier


# logging setup
logger = logging.getLogger("weka.timeseries")


class TSForecaster(OptionHandler):
    """
    Wrapper class for timeseries forecasters.
    """

    def __init__(self, classname="weka.classifiers.timeseries.WekaForecaster", jobject=None, options=None):
        """
        Initializes the specified timeseries forecaster using either the classname or the supplied JB_Object.

        :param classname: the classname of the timeseries forecaster
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = TSForecaster.new_instance(classname, options)
            if jobject is None:
                raise Exception(
                    "Failed to instantiate forecaster '%s' - is package 'timeseriesForecasting' installed and jvm started with package support?" % classname)
        self.enforce_type(jobject, "weka.classifiers.timeseries.TSForecaster")
        super(TSForecaster, self).__init__(jobject=jobject, options=options)
        #self.__forecast = javabridge.make_call(self.jobject, "forecast", "(I[Ljava/lang/Object;)Ljava/util/List;")

    @property
    def fields_to_forecast(self):
        """
        Returns the fields to forecast.

        :return: the fields
        :rtype: str
        """
        return javabridge.call(self.jobject, "getFieldsToForecast", "()Ljava/lang/String;")

    @fields_to_forecast.setter
    def fields_to_forecast(self, fields):
        """
        Sets the fields to forecast.

        :param fields: the comma-separated string or list of fields to forecast
        :type fields: str or list
        """
        if isinstance(fields, list):
            fields = ",".join(fields)
        javabridge.call(self.jobject, "setFieldsToForecast", "(Ljava/lang/String;)V", fields)


class WekaForecaster(TSForecaster):
    """
    Wrapper class for Weka timeseries forecasters.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes a Weka timeseries forecaster.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        super(WekaForecaster, self).__init__(classname="weka.classifiers.timeseries.WekaForecaster", jobject=jobject, options=options)

    @property
    def base_forecaster(self):
        """
        Returns the base forecaster.

        ;return: the base forecaster
        :rtype: Classifier
        """
        return Classifier(jobject=javabridge.call(self.jobject, "getBaseForecaster", "()Lweka/classifiers/Classifier;"))

    @base_forecaster.setter
    def base_forecaster(self, base_forecaster):
        """
        Sets the base forecaster.

        :param base_forecaster: the base forecaster to use
        :type base_forecaster: Classifier
        """
        javabridge.call(self.jobject, "setBaseForecaster", "(Lweka/classifiers/Classifier;)V", base_forecaster.jobject)


class TSEvalModule(JavaObject):
    """
    Wrapper for TSEvalModule objects.
    """

    def __init__(self, jobject):
        """
        Initializes the evaluation module.

        :param jobject: the object to initialize with
        :type jobject: JB_Object
        """
        super(TSEvalModule, self).__init__(jobject)

    def reset(self):
        """
        Resets the module.
        """
        javabridge.call(self.jobject, "reset", "()V")

    @property
    def eval_name(self):
        """
        Returns the name.
        """
        return javabridge.call(self.jobject, "getEvalName", "()Ljava/lang/String;")

    @property
    def description(self):
        """
        Returns the description.
        """
        return javabridge.call(self.jobject, "getDescription", "()Ljava/lang/String;")

    @property
    def definition(self):
        """
        Returns the description.
        """
        return javabridge.call(self.jobject, "getDefinition", "()Ljava/lang/String;")

    @property
    def target_fields(self):
        """
        Returns the list of target fields.

        :return: the list of target fields
        :rtype: list
        """
        objs = javabridge.call(self.jobject, "getTargetFields", "()Ljava/util/List;")
        if objs is None:
            return []
        objs = javabridge.get_collection_wrapper(objs)
        return [str(x) for x in objs]

    @target_fields.setter
    def target_fields(self, fields):
        """
        Sets the list of target fields.

        :param fields: the list of target fields
        :type fields: list
        """
        javabridge.call(self.jobject, "setTargetFields", "(Ljava/util/List;)V", fields)

    @property
    def summary(self):
        """
        Returns the description.
        """
        return javabridge.call(self.jobject, "toSummaryString", "()Ljava/lang/String;")

    def __str__(self):
        """
        Returns the name.
        """
        return self.eval_name

    @classmethod
    def module_list(cls):
        """
        Evaluates the classifier with the given options.

        :param classifier: the classifier instance to use
        :type classifier: Classifier
        :param args: the command-line arguments to use
        :type args: list
        :return: the evaluation string
        :rtype: str
        """
        result = []
        objs = javabridge.get_collection_wrapper(javabridge.static_call(
            "Lweka/classifiers/timeseries/eval/TSEvalModuleHelper;", "getModuleList",
            "()Ljava/util/List;"))
        for obj in objs:
            result.append(TSEvalModule(obj))
        return result

    @classmethod
    def module(cls, name):
        """
        Returns the module with the specified name.

        :param name: the name of the module to return
        :type name: str
        :return: the TSEvalModule object
        :rtype: TSEvalModule
        """
        return TSEvalModule(javabridge.static_call(
            "Lweka/classifiers/timeseries/eval/TSEvalModuleHelper;", "getModule",
            "(Ljava/lang/String;)Ljava/lang/Object;", name))


class ErrorModule(TSEvalModule):
    """
    Wrapper for ErrorModule objects.
    """

    def __init__(self, jobject):
        """
        Initializes the error module.

        :param jobject: the object to initialize with
        :type jobject: JB_Object
        """
        super(ErrorModule, self).__init__(jobject)


class TSEvaluation(JavaObject):
    """
    Evaluation class for timeseries forecasters.
    """

    def __init__(self, train, test_split_size=33.0, test=None):
        """
        Initializes a TSEvaluation object.

        :param train: the training data to use
        :type train: Instances
        :param test_split_size: the number or percentage of instances to hold out from the end of the training data to be test data.
        :type test_split_size: float
        :param test: the explicit test set to use, overrides the split size
        :type test: Instances
        """
        if test is None:
            jobject = javabridge.static_call(
                "Lweka/classifiers/timeseries/eval/TSEvaluationHelper;", "newInstance",
                "(Lweka/core/Instances;D)Ljava/lang/Object;",
                train.jobject, test_split_size)
        else:
            jobject = javabridge.static_call(
                "Lweka/classifiers/timeseries/eval/TSEvaluationHelper;", "newInstance",
                "(Lweka/core/Instances;Lweka/core/Instances;)Ljava/lang/Object;",
                train.jobject, test.jobject)
        super(TSEvaluation, self).__init__(jobject)

        # set up variables
        self._horizon = None
        self._rebuild_model_after_each_test_forecast_step = None

        # initialize with values from Java class
        self.horizon = 1
        self.rebuild_model_after_each_test_forecast_step = False

    @property
    def training_data(self):
        """
        Returns the training data.

        :return: the training data
        :rtype: Instances
        """
        return Instances(javabridge.call(self.jobject, "getTrainingData", "()Lweka/core/Instances;"))

    @training_data.setter
    def training_data(self, data):
        """
        Sets the training data.

        :param data: the training data
        :type data: Instances
        """
        javabridge.call(self.jobject, "setTrainingData", "(Lweka/core/Instances;)V", data.jobject)

    @property
    def test_data(self):
        """
        Returns the test data.

        :return: the test data
        :rtype: Instances
        """
        return Instances(javabridge.call(self.jobject, "getTestData", "()Lweka/core/Instances;"))

    @test_data.setter
    def test_data(self, data):
        """
        Sets the test data.

        :param data: the test data
        :type data: Instances
        """
        javabridge.call(self.jobject, "setTestData", "(Lweka/core/Instances;)V", data.jobject)

    @property
    def evaluate_on_training_data(self):
        """
        Returns whether to evaluate on the training data.

        :return: whether to evaluate
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getEvaluateOnTrainingData", "()Z")

    @evaluate_on_training_data.setter
    def evaluate_on_training_data(self, evaluate):
        """
        Sets whether whether to evaluate on to training data.

        :param evaluate: whether to evaluate
        :type evaluate: bool
        """
        javabridge.call(self.jobject, "setEvaluateOnTrainingData", "(Z)V", evaluate)

    @property
    def evaluate_on_test_data(self):
        """
        Returns whether to evaluate on the test data.

        :return: whether to evaluate
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getEvaluateOnTestData", "()Z")

    @evaluate_on_test_data.setter
    def evaluate_on_test_data(self, evaluate):
        """
        Sets whether whether to evaluate on to test data.

        :param evaluate: whether to evaluate
        :type evaluate: bool
        """
        javabridge.call(self.jobject, "setEvaluateOnTestData", "(Z)V", evaluate)

    @property
    def horizon(self):
        """
        Returns the number of steps to predict into the future.

        :return: the number of steps
        :rtype: int
        """
        return self._horizon

    @horizon.setter
    def horizon(self, steps):
        """
        Sets the number of steps to predict into the future.

        :param steps: the number of steps
        :type steps: int
        """
        javabridge.call(self.jobject, "setHorizon", "(I)V", steps)
        self._horizon = steps

    @property
    def prime_window_size(self):
        """
        Returns the size of the priming window, ie the number of historical instances to present before making a forecast.

        :return: the size
        :rtype: int
        """
        return javabridge.call(self.jobject, "getPrimeWindowSize", "()I")

    @prime_window_size.setter
    def prime_window_size(self, size):
        """
        Sets the size of the priming window, ie the number of historical instances to present before making a forecast.

        :param size: the size
        :type size: int
        """
        javabridge.call(self.jobject, "setPrimeWindowSize", "(I)V", size)

    @property
    def prime_for_test_data_with_test_data(self):
        """
        Returns whether evaluation for test data should begin by priming with the first
        x test data instances and then forecasting from step x + 1. This is the
        only option if there is no training data and a model has been deserialized
        from disk. If we have training data, and it occurs immediately before the
        test data in time, then we can prime with the last x instances from the
        training data.

        :return: whether to prime
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getPrimeForTestDataWithTestData", "()Z")

    @prime_for_test_data_with_test_data.setter
    def prime_for_test_data_with_test_data(self, prime):
        """
        Sets whether evaluation for test data should begin by priming with the first
        x test data instances and then forecasting from step x + 1. This is the
        only option if there is no training data and a model has been deserialized
        from disk. If we have training data, and it occurs immediately before the
        test data in time, then we can prime with the last x instances from the
        training data.

        :param prime: whether to prime
        :type prime: bool
        """
        javabridge.call(self.jobject, "setPrimeForTestDataWithTestData", "(Z)V", prime)

    @property
    def rebuild_model_after_each_test_forecast_step(self):
        """
        Returns whether the forecasting model should be rebuilt after each forecasting
        step on the test data using both the training data and test data up to the
        current instance.

        :return: whether to rebuild
        :rtype: bool
        """
        return self._rebuild_model_after_each_test_forecast_step

    @rebuild_model_after_each_test_forecast_step.setter
    def rebuild_model_after_each_test_forecast_step(self, rebuild):
        """
        Sets whether the forecasting model should be rebuilt after each forecasting
        step on the test data using both the training data and test data up to the
        current instance.

        :param rebuild: whether to rebuild
        :return: bool
        """
        javabridge.call(self.jobject, "setRebuildModelAfterEachTestForecastStep", "(Z)V", rebuild)
        self._rebuild_model_after_each_test_forecast_step = rebuild

    @property
    def forecast_future(self):
        """
        Returns whether we should generate a future forecast beyond the end of the
        training and/or test data.

        :return: whether to prime
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getForecastFuture", "()Z")

    @forecast_future.setter
    def forecast_future(self, prime):
        """
        Sets whether we should generate a future forecast beyond the end of the
        training and/or test data.

        :param prime: whether to prime
        :type prime: bool
        """
        javabridge.call(self.jobject, "setForecastFuture", "(Z)V", prime)

    @property
    def evaluation_modules(self):
        """
        Returns the list of evaluation modules in use.

        :return: list of TSEvalModule object
        :rtype: list
        """
        result = []
        objs = javabridge.get_collection_wrapper(javabridge.call(self.jobject, "getEvaluationModules", "()Ljava/util/List;"))
        for obj in objs:
            result.append(TSEvalModule(obj))
        return result

    @evaluation_modules.setter
    def evaluation_modules(self, modules):
        """
        Sets the evaluation modules to use (comma-separated list or list of TSEvalModule/str objects).

        :param modules: the evaluation modules (str or list)
        :type modules: str
        """
        if isinstance(modules, list):
            modules = [str(module) for module in modules]
            modules.remove("Error")  # requires manual removal
            modules = ",".join(modules)
        javabridge.call(self.jobject, "setEvaluationModules", "(Ljava/lang/String;)V", modules)

    def __str__(self):
        """
        Prints a simple summary of the evaluation setup.

        :return: the summary
        :rtype: str
        """
        eval_modules = [x.eval_name for x in self.evaluation_modules]

        return "=== Evaluation setup ===\n\n" \
               + "Relation: " + self.training_data.relationname + "\n" \
               + "# Training instances: " + str(self.training_data.num_instances) + "\n" \
               + "# Test instances: " + str(self.test_data.num_instances) + "\n" \
               + "Evaluate on training data: " + str(self.evaluate_on_training_data) + "\n" \
               + "Evaluate on test data: " + str(self.evaluate_on_test_data) + "\n" \
               + "Horizon: " + str(self.horizon) + "\n" \
               + "Prime window size: " + str(self.prime_window_size) + "\n" \
               + "Prime for test data with test data: " + str(self.prime_for_test_data_with_test_data) + "\n" \
               + "Rebuild model after each test forecast step: " + str(self.rebuild_model_after_each_test_forecast_step) + "\n" \
               + "Forecast future: " + str(self.forecast_future) + "\n" \
               + "Evaluation modules: " + ", ".join(eval_modules) + "\n" \
               + "\n"

    def evaluate(self, forecaster, build_model=True):
        """
        Evaluates the forecaster.

        :param forecaster: the forecaster to evaluate
        :type forecaster: TSForecaster
        :param build_model: whether to build the model as well
        :type build_model: bool
        """
        javabridge.call(
            self.jobject, "evaluateForecaster",
            "(Lweka/classifiers/timeseries/TSForecaster;Z[Ljava/io/PrintStream;)V",
            forecaster.jobject, build_model, [])

    def predictions_for_training_data(self, step_number):
        """
        Predictions for all targets for the specified step number on the training data.

        :param step_number: number of the step into the future to return predictions for
        :type step_number: int
        """
        return ErrorModule(javabridge.call(
            self.jobject, "getPredictionsForTrainingData",
            "(I)Lweka/classifiers/timeseries/eval/ErrorModule;",
            step_number))

    def predictions_for_test_data(self, step_number):
        """
        Predictions for all targets for the specified step number on the test data.

        :param step_number: number of the step into the future to return predictions for
        :type step_number: int
        """
        return ErrorModule(javabridge.call(
            self.jobject, "getPredictionsForTestData",
            "(I)Lweka/classifiers/timeseries/eval/ErrorModule;",
            step_number))

    def print_future_forecast_on_training_data(self, forecaster):
        """
        Print the forecasted values (for all targets) beyond the end of the training data.

        :param forecaster: the forecaster to use
        :type forecaster: TSForecaster
        :return: the forecasted values
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "printFutureTrainingForecast",
            "(Lweka/classifiers/timeseries/TSForecaster;)Ljava/lang/String;", forecaster.jobject)

    def print_future_forecast_on_test_data(self, forecaster):
        """
        Print the forecasted values (for all targets) beyond the end of the test data.

        :param forecaster: the forecaster to use
        :type forecaster: TSForecaster
        :return: the forecasted values
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "printFutureTestForecast",
            "(Lweka/classifiers/timeseries/TSForecaster;)Ljava/lang/String;", forecaster.jobject)

    def print_predictions_for_training_data(self, title, target_name, step_ahead, instance_number_offset=0):
        """
        Print the predictions for a given target at a given step-ahead level on the training data.

        :param title: the title for the output
        :type title: str
        :param target_name: the name of the target to print predictions for
        :type target_name: str
        :param step_ahead: the step-ahead level - e.g. 3 would print the 3-step-ahead predictions
        :type step_ahead: int
        :param instance_number_offset: the offset from the start of the training data from which to print actual and predicted values
        :type instance_number_offset: int
        :return: the predicted/actual values
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "printPredictionsForTrainingData",
            "(Ljava/lang/String;Ljava/lang/String;II)Ljava/lang/String;", title, target_name, step_ahead, instance_number_offset)

    def print_predictions_for_test_data(self, title, target_name, step_ahead, instance_number_offset=0):
        """
        Print the predictions for a given target at a given step-ahead level on the test data.

        :param title: the title for the output
        :type title: str
        :param target_name: the name of the target to print predictions for
        :type target_name: str
        :param step_ahead: the step-ahead level - e.g. 3 would print the 3-step-ahead predictions
        :type step_ahead: int
        :param instance_number_offset: the offset from the start of the test data from which to print actual and predicted values
        :type instance_number_offset: int
        :return: the predicted/actual values
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "printPredictionsForTestData",
            "(Ljava/lang/String;Ljava/lang/String;II)Ljava/lang/String;", title, target_name, step_ahead, instance_number_offset)

    def summary(self):
        """
        Generates a summary.

        :return: the summary
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "toSummaryString", "()Ljava/lang/String;")

    @classmethod
    def evaluate_forecaster(cls, forecaster, args):
        """
        Evaluates the forecaster with the given options.

        :param forecaster: the forecaster instance to use
        :type forecaster: TSForecaster
        :param args: the command-line arguments to use
        :type args: list
        """
        javabridge.static_call(
            "Lweka/classifiers/timeseries/eval/TSEvaluation;", "evaluateForecaster",
            "(Lweka/classifiers/timeseries/TSForecaster;[Ljava/lang/String;)Ljava/lang/String;",
            forecaster.jobject, args)
