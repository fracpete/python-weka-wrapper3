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
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import logging
import javabridge
from weka.core.classes import OptionHandler, Range, from_commandline
from weka.core.dataset import Instances
from weka.classifiers import Classifier

# logging setup
logger = logging.getLogger("weka.experiments")


class Experiment(OptionHandler):
    """
    Wrapper class for an experiment.
    """

    def __init__(self, classname="weka.experiment.Experiment", jobject=None, options=None):
        """
        Initializes the specified experiment using either the classname or the supplied JB_Object.

        :param classname: the classname of the experiment
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = Experiment.new_instance(classname)
        super(Experiment, self).__init__(jobject=jobject, options=options)


class SimpleExperiment(OptionHandler):
    """
    Ancestor for simple experiments.

    See following URL for how to use the Experiment API:
    http://weka.wikispaces.com/Using+the+Experiment+API
    """

    def __init__(self, datasets, classifiers, jobject=None, classification=True, runs=10, result=None):
        """
        Initializes the experiment.

        :param datasets: the filenames of datasets to use in the experiment
        :type datasets: list
        :param classifiers: the Classifier objects or commandline strings to use in the experiment
        :type classifiers: list
        :param jobject: the Java Object to use
        :type jobject: JB_Object
        :param classification: whether to perform classification or regression
        :type classification:bool
        :param runs: the number of runs to perform
        :type runs: int
        :param result: the filename of the file to store the results in
        :type result: str
        """

        if not jobject is None:
            self.enforce_type(jobject, "weka.experiment.Experiment")
        if jobject is None:
            jobject = javabridge.make_instance("weka/experiment/Experiment", "()V")

        self.classification = classification
        self.runs = runs
        self.datasets = datasets[:]
        self.classifiers = classifiers[:]
        self.result = result
        super(SimpleExperiment, self).__init__(jobject=jobject)

    def configure_splitevaluator(self):
        """
        Configures and returns the SplitEvaluator and Classifier instance as tuple.

        :return: evaluator and classifier
        :rtype: tuple
        """
        if self.classification:
            speval = javabridge.make_instance("weka/experiment/ClassifierSplitEvaluator", "()V")
        else:
            speval = javabridge.make_instance("weka/experiment/RegressionSplitEvaluator", "()V")
        classifier = javabridge.call(speval, "getClassifier", "()Lweka/classifiers/Classifier;")
        return speval, classifier

    def configure_resultproducer(self):
        """
        Configures and returns the ResultProducer and PropertyPath as tuple.

        :return: producer and property path
        :rtype: tuple
        """
        raise Exception("Not implemented!")

    def setup(self):
        """
        Initializes the experiment.
        """
        # basic options
        javabridge.call(
            self.jobject, "setPropertyArray", "(Ljava/lang/Object;)V",
            javabridge.get_env().make_object_array(0, javabridge.get_env().find_class("weka/classifiers/Classifier")))
        javabridge.call(
            self.jobject, "setUsePropertyIterator", "(Z)V", True)
        javabridge.call(
            self.jobject, "setRunLower", "(I)V", 1)
        javabridge.call(
            self.jobject, "setRunUpper", "(I)V", self.runs)

        # setup result producer
        rproducer, prop_path = self.configure_resultproducer()
        javabridge.call(
            self.jobject, "setResultProducer", "(Lweka/experiment/ResultProducer;)V", rproducer)
        javabridge.call(
            self.jobject, "setPropertyPath", "([Lweka/experiment/PropertyNode;)V", prop_path)

        # classifiers
        classifiers = javabridge.get_env().make_object_array(
            len(self.classifiers), javabridge.get_env().find_class("weka/classifiers/Classifier"))
        for i, classifier in enumerate(self.classifiers):
            if type(classifier) is Classifier:
                javabridge.get_env().set_object_array_element(
                    classifiers, i, classifier.jobject)
            else:
                javabridge.get_env().set_object_array_element(
                    classifiers, i, from_commandline(classifier).jobject)
        javabridge.call(
            self.jobject, "setPropertyArray", "(Ljava/lang/Object;)V",
            classifiers)

        # datasets
        datasets = javabridge.make_instance("javax/swing/DefaultListModel", "()V")
        for dataset in self.datasets:
            f = javabridge.make_instance("java/io/File", "(Ljava/lang/String;)V", dataset)
            javabridge.call(datasets, "addElement", "(Ljava/lang/Object;)V", f)
        javabridge.call(
            self.jobject, "setDatasets", "(Ljavax/swing/DefaultListModel;)V", datasets)

        # output file
        if str(self.result).lower().endswith(".arff"):
            rlistener = javabridge.make_instance("weka/experiment/InstancesResultListener", "()V")
        elif str(self.result).lower().endswith(".csv"):
            rlistener = javabridge.make_instance("weka/experiment/CSVResultListener", "()V")
        else:
            raise Exception("Unhandled output format for results: " + self.result)
        rfile = javabridge.make_instance("java/io/File", "(Ljava/lang/String;)V", self.result)
        javabridge.call(
            rlistener, "setOutputFile", "(Ljava/io/File;)V", rfile)
        javabridge.call(
            self.jobject, "setResultListener", "(Lweka/experiment/ResultListener;)V", rlistener)

    def run(self):
        """
        Executes the experiment.
        """
        logger.info("Initializing...")
        javabridge.call(self.jobject, "initialize", "()V")
        logger.info("Running...")
        javabridge.call(self.jobject, "runExperiment", "()V")
        logger.info("Finished...")
        javabridge.call(self.jobject, "postProcess", "()V")

    def experiment(self):
        """
        Returns the internal experiment, if set up, otherwise None.

        :return: the internal experiment
        :rtype: Experiment
        """
        if self.jobject is None:
            return None
        else:
            return Experiment(jobject=self.jobject)

    @classmethod
    def load(cls, filename):
        """
        Loads the experiment from disk.

        :param filename: the filename of the experiment to load
        :type filename: str
        :return: the experiment
        :rtype: Experiment
        """
        jobject = javabridge.static_call(
            "weka/experiment/Experiment", "read", "(Ljava/lang/String;)Lweka/experiment/Experiment;",
            filename)
        return Experiment(jobject=jobject)

    @classmethod
    def save(cls, filename, experiment):
        """
        Saves the experiment to disk.

        :param filename: the filename to save the experiment to
        :type filename: str
        :param experiment: the Experiment to save
        :type experiment: Experiment
        """
        javabridge.static_call(
            "weka/experiment/Experiment", "write", "(Ljava/lang/String;Lweka/experiment/Experiment;)V",
            filename, experiment.jobject)


class SimpleCrossValidationExperiment(SimpleExperiment):
    """
    Performs a simple cross-validation experiment. Can output the results either in ARFF or CSV.
    """

    def __init__(self, datasets, classifiers, classification=True, runs=10, folds=10, result=None):
        """
        Initializes the experiment.

        :param datasets: the filenames of datasets to use in the experiment
        :type datasets: list
        :param classifiers: the Classifier objects to use in the experiment
        :type classifiers: list
        :param classification: whether to perform classification
        :type classification: bool
        :param runs: the number of runs to perform
        :type runs: int
        :param folds: the number folds to use for CV
        :type folds: int
        :param result: the filename of the file to store the results in
        :type result: str
        """

        if runs < 1:
            raise Exception("Number of runs must be at least 1!")
        if folds < 2:
            raise Exception("Number of folds must be at least 2!")
        if len(datasets) == 0:
            raise Exception("No datasets provided!")
        if len(classifiers) == 0:
            raise Exception("No classifiers provided!")
        if result is None:
            raise Exception("No filename for results provided!")

        super(SimpleCrossValidationExperiment, self).__init__(
            classification=classification, runs=runs, datasets=datasets,
            classifiers=classifiers, result=result)

        self.folds = folds

    def configure_resultproducer(self):
        """
        Configures and returns the ResultProducer and PropertyPath as tuple.

        :return: producer and property path
        :rtype: tuple
        """
        rproducer = javabridge.make_instance("weka/experiment/CrossValidationResultProducer", "()V")
        javabridge.call(rproducer, "setNumFolds", "(I)V", self.folds)
        speval, classifier = self.configure_splitevaluator()
        javabridge.call(rproducer, "setSplitEvaluator", "(Lweka/experiment/SplitEvaluator;)V", speval)
        prop_path = javabridge.get_env().make_object_array(
            2, javabridge.get_env().find_class("weka/experiment/PropertyNode"))
        cls = javabridge.get_env().find_class("weka/experiment/CrossValidationResultProducer")
        desc = javabridge.make_instance(
            "java/beans/PropertyDescriptor", "(Ljava/lang/String;Ljava/lang/Class;)V", "splitEvaluator", cls)
        node = javabridge.make_instance(
            "weka/experiment/PropertyNode", "(Ljava/lang/Object;Ljava/beans/PropertyDescriptor;Ljava/lang/Class;)V",
            speval, desc, cls)
        javabridge.get_env().set_object_array_element(prop_path, 0, node)
        cls = javabridge.get_env().get_object_class(speval)
        desc = javabridge.make_instance(
            "java/beans/PropertyDescriptor", "(Ljava/lang/String;Ljava/lang/Class;)V", "classifier", cls)
        node = javabridge.make_instance(
            "weka/experiment/PropertyNode", "(Ljava/lang/Object;Ljava/beans/PropertyDescriptor;Ljava/lang/Class;)V",
            javabridge.call(speval, "getClass", "()Ljava/lang/Class;"), desc, cls)
        javabridge.get_env().set_object_array_element(prop_path, 1, node)

        return rproducer, prop_path


class SimpleRandomSplitExperiment(SimpleExperiment):
    """
    Performs a simple random split experiment. Can output the results either in ARFF or CSV.
    """

    def __init__(self, datasets, classifiers, classification=True, runs=10, percentage=66.6, preserve_order=False,
                 result=None):
        """
        Initializes the experiment.

        :param classification: whether to perform classification or regression
        :type classification: bool
        :param runs: the number of runs to perform
        :type runs: int
        :param percentage: the percentage to use for training
        :type percentage: float
        :param preserve_order: whether to preserve the order in the datasets
        :type preserve_order: bool
        :param datasets: the filenames of datasets to use in the experiment
        :type datasets: list
        :param classifiers: the Classifier objects to use in the experiment
        :type classifiers: list
        :param result: the filename of the file to store the results in
        :type result: str
        """

        if runs < 1:
            raise Exception("Number of runs must be at least 1!")
        if percentage <= 0:
            raise Exception("Percentage for training must be >0!")
        if percentage >= 100:
            raise Exception("Percentage for training must be <100!")
        if len(datasets) == 0:
            raise Exception("No datasets provided!")
        if len(classifiers) == 0:
            raise Exception("No classifiers provided!")
        if result is None:
            raise Exception("No filename for results provided!")

        super(SimpleRandomSplitExperiment, self).__init__(
            classification=classification, runs=runs, datasets=datasets,
            classifiers=classifiers, result=result)

        self.percentage = percentage
        self.preserve_order = preserve_order

    def configure_resultproducer(self):
        """
        Configures and returns the ResultProducer and PropertyPath as tuple.

        :return: producer and property path
        :rtype: tuple
        """
        rproducer = javabridge.make_instance("weka/experiment/RandomSplitResultProducer", "()V")
        javabridge.call(rproducer, "setRandomizeData", "(Z)V", not self.preserve_order)
        javabridge.call(rproducer, "setTrainPercent", "(D)V", self.percentage)
        speval, classifier = self.configure_splitevaluator()
        javabridge.call(rproducer, "setSplitEvaluator", "(Lweka/experiment/SplitEvaluator;)V", speval)
        prop_path = javabridge.get_env().make_object_array(
            2, javabridge.get_env().find_class("weka/experiment/PropertyNode"))
        cls = javabridge.get_env().find_class("weka/experiment/RandomSplitResultProducer")
        desc = javabridge.make_instance(
            "java/beans/PropertyDescriptor", "(Ljava/lang/String;Ljava/lang/Class;)V", "splitEvaluator", cls)
        node = javabridge.make_instance(
            "weka/experiment/PropertyNode", "(Ljava/lang/Object;Ljava/beans/PropertyDescriptor;Ljava/lang/Class;)V",
            speval, desc, cls)
        javabridge.get_env().set_object_array_element(prop_path, 0, node)
        cls = javabridge.get_env().get_object_class(speval)
        desc = javabridge.make_instance(
            "java/beans/PropertyDescriptor", "(Ljava/lang/String;Ljava/lang/Class;)V", "classifier", cls)
        node = javabridge.make_instance(
            "weka/experiment/PropertyNode", "(Ljava/lang/Object;Ljava/beans/PropertyDescriptor;Ljava/lang/Class;)V",
            javabridge.call(speval, "getClass", "()Ljava/lang/Class;"), desc, cls)
        javabridge.get_env().set_object_array_element(prop_path, 1, node)

        return rproducer, prop_path


class ResultMatrix(OptionHandler):
    """
    For generating results from an Experiment run.
    """

    def __init__(self, classname="weka.experiment.ResultMatrixPlainText", jobject=None, options=None):
        """
        Initializes the specified ResultMatrix using either the classname or the supplied JB_Object.

        :param classname: the classname of the ResultMatrix
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to use
        :type options: list
        """
        if jobject is None:
            jobject = ResultMatrix.new_instance(classname)
        self.enforce_type(jobject, "weka.experiment.ResultMatrix")
        super(ResultMatrix, self).__init__(jobject=jobject, options=options)

    @property
    def rows(self):
        """
        Returns the row count.

        :return: the count
        :rtype: int
        """
        return javabridge.call(self.jobject, "getRowCount", "()I")

    @property
    def columns(self):
        """
        Returns the column count.

        :return: the count
        :rtype: int
        """
        return javabridge.call(self.jobject, "getColCount", "()I")

    def is_col_hidden(self, index):
        """
        Returns whether the column is hidden.

        :param index: the 0-based column index
        :type index: int
        :return: true if hidden
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getColHidden", "(I)Z", index)

    def hide_col(self, index):
        """
        Hides the column.

        :param index: the 0-based column index
        :type index: int
        """
        javabridge.call(self.jobject, "setColHidden", "(IZ)V", index, True)

    def show_col(self, index):
        """
        Shows the column.

        :param index: the 0-based column index
        :type index: int
        """
        javabridge.call(self.jobject, "setColHidden", "(IZ)V", index, False)

    def is_row_hidden(self, index):
        """
        Returns whether the row is hidden.

        :param index: the 0-based row index
        :type index: int
        :return: true if hidden
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getRowHidden", "(I)Z", index)

    def hide_row(self, index):
        """
        Hides the row.

        :param index: the 0-based row index
        :type index: int
        """
        javabridge.call(self.jobject, "setRowHidden", "(IZ)V", index, True)

    def show_row(self, index):
        """
        Shows the row.

        :param index: the 0-based row index
        :type index: int
        """
        javabridge.call(self.jobject, "setRowHidden", "(IZ)V", index, False)

    def get_row_name(self, index):
        """
        Returns the row name.

        :param index: the 0-based row index
        :type index: int
        :return: the row name, None if invalid index
        :rtype: str
        """
        return javabridge.call(self.jobject, "getRowName", "(I)Ljava/lang/String;", index)

    def set_row_name(self, index, name):
        """
        Sets the row name.

        :param index: the 0-based row index
        :type index: int
        :param name: the name of the row
        :type name: str
        """
        javabridge.call(self.jobject, "setRowName", "(ILjava/lang/String;)V", index, name)

    def get_col_name(self, index):
        """
        Returns the column name.

        :param index: the 0-based row index
        :type index: int
        :return: the column name, None if invalid index
        :rtype: str
        """
        return javabridge.call(self.jobject, "getColName", "(I)Ljava/lang/String;", index)

    def set_col_name(self, index, name):
        """
        Sets the column name.

        :param index: the 0-based row index
        :type index: int
        :param name: the name of the column
        :type name: str
        """
        javabridge.call(self.jobject, "setColName", "(ILjava/lang/String;)V", index, name)

    def get_mean(self, col, row):
        """
        Returns the mean at this location (if valid location).

        :param col: the 0-based column index
        :type col: int
        :param row: the 0-based row index
        :type row: int
        :return: the mean
        :rtype: float
        """
        return javabridge.call(self.jobject, "getMean", "(II)D", col, row)

    def set_mean(self, col, row, mean):
        """
        Sets the mean at this location (if valid location).

        :param col: the 0-based column index
        :type col: int
        :param row: the 0-based row index
        :type row: int
        :param mean: the mean to set
        :type mean: float
        """
        javabridge.call(self.jobject, "setMean", "(IID)V", col, row, mean)

    def get_stdev(self, col, row):
        """
        Returns the standard deviation at this location (if valid location).

        :param col: the 0-based column index
        :type col: int
        :param row: the 0-based row index
        :type row: int
        :return: the standard deviation
        :rtype: float
        """
        return javabridge.call(self.jobject, "getStdDev", "(II)D", col, row)

    def set_stdev(self, col, row, stdev):
        """
        Sets the standard deviation at this location (if valid location).

        :param col: the 0-based column index
        :type col: int
        :param row: the 0-based row index
        :type row: int
        :param stdev: the standard deviation to set
        :type stdev: float
        """
        javabridge.call(self.jobject, "setStdDev", "(IID)V", col, row, stdev)

    def average(self, col):
        """
        Returns the average mean at this location (if valid location).

        :param col: the 0-based column index
        :type col: int
        :return: the mean
        :rtype: float
        """
        return javabridge.call(self.jobject, "getAverage", "(I)D", col)

    def to_string_matrix(self):
        """
        Returns the matrix as a string.

        :return: the generated output
        :rtype: str
        """
        return javabridge.call(self.jobject, "toStringMatrix", "()V")

    def to_string_key(self):
        """
        Returns a key for all the col names, for better readability if the names got cut off.

        :return: the key
        :rtype: str
        """
        return javabridge.call(self.jobject, "toStringKey", "()V")

    def to_string_header(self):
        """
        Returns the header of the matrix as a string.

        :return: the header
        :rtype: str
        """
        return javabridge.call(self.jobject, "toStringHeader", "()V")

    def to_string_summary(self):
        """
        returns the summary as string.

        :return: the summary
        :rtype: str
        """
        return javabridge.call(self.jobject, "toStringSummary", "()V")

    def to_string_ranking(self):
        """
        Returns the ranking in a string representation.

        :return: the ranking
        :rtype: str
        """
        return javabridge.call(self.jobject, "toStringRanking", "()V")


class Tester(OptionHandler):
    """
    For generating statistical results from an experiment.
    """

    def __init__(self, classname="weka.experiment.PairedCorrectedTTester", jobject=None, options=None):
        """
        Initializes the specified tester using either the classname or the supplied JB_Object.

        :param classname: the classname of the tester
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = Tester.new_instance(classname)
        self.enforce_type(jobject, "weka.experiment.Tester")
        self.columns_determined = False
        self._dataset_columns = ["Key_Dataset"]
        self._run_column = "Key_Run"
        self._fold_column = "Key_Fold"
        self._result_columns = ["Key_Scheme", "Key_Scheme_options", "Key_Scheme_version_ID"]
        super(Tester, self).__init__(jobject=jobject, options=options)

    @property
    def resultmatrix(self):
        """
        Returns the ResultMatrix instance in use.

        :return: the matrix in use
        :rtype: ResultMatrix
        """
        return ResultMatrix(
            jobject=javabridge.call(self.jobject, "getResultMatrix", "()Lweka/experiment/ResultMatrix;"))

    @resultmatrix.setter
    def resultmatrix(self, matrix):
        """
        Sets the ResultMatrix to use.

        :param matrix: the ResultMatrix instance to use
        :type matrix: ResultMatrix
        """
        javabridge.call(self.jobject, "setResultMatrix", "(Lweka/experiment/ResultMatrix;)V", matrix.jobject)

    @property
    def instances(self):
        """
        Returns the data used in the analysis.

        :return: the data in use
        :rtype: Instances
        """
        inst = javabridge.call(self.jobject, "getInstances", "()Lweka/core/Instances;")
        if inst is None:
            return None
        else:
            return Instances(inst)

    @instances.setter
    def instances(self, data):
        """
        Sets the data to use for analysis.

        :param data: the Instances to analyze
        :type data: Instances
        """
        javabridge.call(self.jobject, "setInstances", "(Lweka/core/Instances;)V", data.jobject)
        self.columns_determined = False

    @property
    def dataset_columns(self):
        """
        Returns the list of column names that identify uniquely a dataset.

        :return: the list of attributes names
        :rtype: list
        """
        return self._dataset_columns

    @dataset_columns.setter
    def dataset_columns(self, col_names):
        """
        Sets the list of column names that identify uniquely a dataset.

        :param col_names: the list of attribute names
        :type col_names: list
        """
        self._dataset_columns = col_names[:]

    @property
    def run_column(self):
        """
        Returns the column name that holds the Run number.

        :return: the attribute name
        :rtype: str
        """
        return self._run_column

    @run_column.setter
    def run_column(self, col_name):
        """
        Sets the column name that holds the Run number.

        :param col_name: the attribute name
        :type col_name: str
        """
        self._run_column = col_name

    @property
    def fold_column(self):
        """
        Returns the column name that holds the Fold number.

        :return: the attribute name
        :rtype: str
        """
        return self._fold_column

    @fold_column.setter
    def fold_column(self, col_name):
        """
        Sets the column name that holds the Fold number.

        :param col_name: the attribute name
        :type col_name: str
        """
        self._fold_column = col_name

    @property
    def result_columns(self):
        """
        Returns the list of column names that identify uniquely a result (eg classifier + options + ID).

        :return: the list of attribute names
        :rtype: list
        """
        return self._result_columns

    @result_columns.setter
    def result_columns(self, col_names):
        """
        Sets the list of column names that identify uniquely a result (eg classifier + options + ID).

        :param col_names: the list of attribute names
        :type col_names: list
        """
        self._result_columns = col_names[:]

    def init_columns(self):
        """
        Sets the column indices based on the supplied names if necessary.
        """
        if self.columns_determined:
            return
        data = self.instances
        if data is None:
            print("No instances set, cannot determine columns!")
            return

        # dataset
        if self.dataset_columns is None:
            raise Exception("No dataset columns set!")
        cols = ""
        for name in self.dataset_columns:
            att = data.attribute_by_name(name)
            if att is None:
                raise Exception("Dataset column not found: " + name)
            if len(cols) > 0:
                cols += ","
            cols += str(att.index + 1)
        javabridge.call(
            self.jobject, "setDatasetKeyColumns", "(Lweka/core/Range;)V", Range(ranges=cols).jobject)

        # run
        if self.run_column is None:
            raise Exception("No run columnn set!")
        att = data.attribute_by_name(self.run_column)
        if att is None:
            raise Exception("Run column not found: " + self.run_column)
        javabridge.call(
            self.jobject, "setRunColumn", "(I)V", att.index)

        # fold
        if not self.fold_column is None:
            att = data.attribute_by_name(self.fold_column)
            if att is None:
                index = -1
            else:
                index = att.index
            javabridge.call(
                self.jobject, "setFoldColumn", "(I)V", index)

        # result
        if self._result_columns is None:
            raise Exception("No reset columns set!")
        cols = ""
        for name in self._result_columns:
            att = data.attribute_by_name(name)
            if att is None:
                raise Exception("Result column not found: " + name)
            if len(cols) > 0:
                cols += ","
            cols += str(att.index + 1)
        javabridge.call(
            self.jobject, "setResultsetKeyColumns", "(Lweka/core/Range;)V", Range(ranges=cols).jobject)

        self.columns_determined = True

    def header(self, comparison_column):
        """
        Creates a "header" string describing the current resultsets.

        :param comparison_column: the index of the column to compare against
        :type comparison_column: int
        :return: the header
        :rtype: str
        """
        self.init_columns()
        return javabridge.call(
            self.jobject, "header", "(I)Ljava/lang/String;", comparison_column)

    def multi_resultset_full(self, base_resultset, comparison_column):
        """
        Creates a comparison table where a base resultset is compared to the other resultsets.

        :param base_resultset: the 0-based index of the base resultset (eg classifier to compare against)
        :type base_resultset: int
        :param comparison_column: the 0-based index of the column to compare against
        :type comparison_column: int
        :return: the comparison
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "multiResultsetFull", "(II)Ljava/lang/String;", base_resultset, comparison_column)

    def multi_resultset_ranking(self, comparison_column):
        """
        Creates a ranking.

        :param comparison_column: the 0-based index of the column to compare against
        :type comparison_column: int
        :return: the ranking
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "multiResultsetRanking", "(I)Ljava/lang/String;", comparison_column)

    def multi_resultset_summary(self, comparison_column):
        """
        Carries out a comparison between all resultsets, counting the number of datsets where one resultset
        outperforms the other.

        :param comparison_column: the 0-based index of the column to compare against
        :type comparison_column: int
        :return: the summary
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "multiResultsetSummary", "(I)Ljava/lang/String;", comparison_column)
