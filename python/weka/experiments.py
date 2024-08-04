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
# Copyright (C) 2014-2024 Fracpete (pythonwekawrapper at gmail dot com)

import logging
from jpype import JClass
from weka.core.classes import OptionHandler, Range, from_commandline, new_array
from weka.core.dataset import Instances
from weka.classifiers import Classifier

# logging setup
logger = logging.getLogger("weka.experiments")
logger.setLevel(logging.INFO)


class Experiment(OptionHandler):
    """
    Wrapper class for an experiment.
    """

    def __init__(self, classname="weka.experiment.Experiment", jobject=None, options=None):
        """
        Initializes the specified experiment using either the classname or the supplied JPype object.

        :param classname: the classname of the experiment
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
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

    def __init__(self, datasets, classifiers, jobject=None, classification=True, runs=10, result=None,
                 class_for_ir_statistics=0, attribute_id=-1, pred_target_column=False):
        """
        Initializes the experiment.

        :param datasets: the filenames of datasets to use in the experiment
        :type datasets: list
        :param classifiers: the Classifier objects or commandline strings to use in the experiment
        :type classifiers: list
        :param jobject: the Java Object to use
        :type jobject: JPype object
        :param classification: whether to perform classification or regression
        :type classification:bool
        :param runs: the number of runs to perform
        :type runs: int
        :param result: the filename of the file to store the results in
        :type result: str
        :param class_for_ir_statistics: the class label index to use IR statistics (classification only)
        :type class_for_ir_statistics: int
        :param attribute_id: the 0-based index of the attribute identifying instances (classification only)
        :type attribute_id: int
        :param pred_target_column: whether to store the predicted and target columns as well (classification only)
        :type pred_target_column: bool
        """

        if not jobject is None:
            self.enforce_type(jobject, "weka.experiment.Experiment")
        if jobject is None:
            jobject = JClass("weka.experiment.Experiment")()

        self.classification = classification
        self.runs = runs
        self.datasets = datasets[:]
        self.classifiers = classifiers[:]
        self.result = result
        self.class_for_ir_statistics = class_for_ir_statistics
        self.attribute_id = attribute_id
        self.pred_target_column = pred_target_column
        super(SimpleExperiment, self).__init__(jobject=jobject)

    def configure_splitevaluator(self):
        """
        Configures and returns the SplitEvaluator and Classifier instance as tuple.

        :return: evaluator and classifier
        :rtype: tuple
        """
        if self.classification:
            speval = JClass("weka.experiment.ClassifierSplitEvaluator")()
            speval.setClassForIRStatistics(self.class_for_ir_statistics)
            speval.setAttributeID(self.attribute_id)
            speval.setPredTargetColumn(self.pred_target_column)
        else:
            speval = JClass("weka.experiment.RegressionSplitEvaluator")()

        classifier = speval.getClassifier()
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
        self.jobject.setPropertyArray(new_array("weka.classifiers.Classifier", 0))
        self.jobject.setUsePropertyIterator(True)
        self.jobject.setRunLower(1)
        self.jobject.setRunUpper(self.runs)

        # setup result producer
        rproducer, prop_path = self.configure_resultproducer()
        self.jobject.setResultProducer(rproducer)
        self.jobject.setPropertyPath(prop_path)

        # classifiers
        classifiers = new_array("weka.classifiers.Classifier", len(self.classifiers))
        for i, classifier in enumerate(self.classifiers):
            if type(classifier) is Classifier:
                classifiers[i] = classifier.jobject
            else:
                classifiers[i] = from_commandline(classifier).jobject
        self.jobject.setPropertyArray(classifiers)

        # datasets
        datasets = JClass("javax.swing.DefaultListModel")()
        for dataset in self.datasets:
            datasets.addElement(JClass("java.io.File")(dataset))
        self.jobject.setDatasets(datasets)

        # output file
        if str(self.result).lower().endswith(".arff"):
            rlistener = JClass("weka.experiment.InstancesResultListener")()
        elif str(self.result).lower().endswith(".csv"):
            rlistener = JClass("weka.experiment.CSVResultListener")()
        else:
            raise Exception("Unhandled output format for results: " + self.result)
        rlistener.setOutputFile(JClass("java.io.File")(self.result))
        self.jobject.setResultListener(rlistener)

    def run(self):
        """
        Executes the experiment.
        """
        logger.info("Initializing...")
        self.jobject.initialize()
        logger.info("Running...")
        self.jobject.runExperiment()
        logger.info("Finished...")
        self.jobject.postProcess()

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
        return Experiment(JClass("weka.experiment.Experiment").read(filename))

    @classmethod
    def save(cls, filename, experiment):
        """
        Saves the experiment to disk.

        :param filename: the filename to save the experiment to
        :type filename: str
        :param experiment: the Experiment to save
        :type experiment: Experiment
        """
        JClass("weka.experiment.Experiment").write(filename, experiment.jobject)


class SimpleCrossValidationExperiment(SimpleExperiment):
    """
    Performs a simple cross-validation experiment. Can output the results either in ARFF or CSV.
    """

    def __init__(self, datasets, classifiers, classification=True, runs=10, folds=10, result=None,
                 class_for_ir_statistics=0, attribute_id=-1, pred_target_column=False):
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
        :param class_for_ir_statistics: the class label index to use IR statistics (classification only)
        :type class_for_ir_statistics: int
        :param attribute_id: the 0-based index of the attribute identifying instances (classification only)
        :type attribute_id: int
        :param pred_target_column: whether to store the predicted and target columns as well (classification only)
        :type pred_target_column: bool
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
            classifiers=classifiers, result=result,
            class_for_ir_statistics=class_for_ir_statistics, attribute_id=attribute_id,
            pred_target_column=pred_target_column)

        self.folds = folds

    def configure_resultproducer(self):
        """
        Configures and returns the ResultProducer and PropertyPath as tuple.

        :return: producer and property path
        :rtype: tuple
        """
        rproducer = JClass("weka.experiment.CrossValidationResultProducer")()
        rproducer.setNumFolds(self.folds)
        speval, classifier = self.configure_splitevaluator()
        rproducer.setSplitEvaluator(speval)
        prop_path = new_array("weka.experiment.PropertyNode", 2)
        cls = JClass("weka.experiment.CrossValidationResultProducer")
        desc = JClass("java.beans.PropertyDescriptor")("splitEvaluator", cls)
        node = JClass("weka.experiment.PropertyNode")(speval, desc, cls)
        prop_path[0] = node
        cls = speval.getClass()
        desc = JClass("java.beans.PropertyDescriptor")("classifier", cls)
        node = JClass("weka.experiment.PropertyNode")(speval.getClass(), desc, cls)
        prop_path[1] = node

        return rproducer, prop_path


class SimpleRandomSplitExperiment(SimpleExperiment):
    """
    Performs a simple random split experiment. Can output the results either in ARFF or CSV.
    """

    def __init__(self, datasets, classifiers, classification=True, runs=10, percentage=66.6, preserve_order=False,
                 result=None, class_for_ir_statistics=0, attribute_id=-1, pred_target_column=False):
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
        :param class_for_ir_statistics: the class label index to use IR statistics (classification only)
        :type class_for_ir_statistics: int
        :param attribute_id: the 0-based index of the attribute identifying instances (classification only)
        :type attribute_id: int
        :param pred_target_column: whether to store the predicted and target columns as well (classification only)
        :type pred_target_column: bool
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
            classifiers=classifiers, result=result,
            class_for_ir_statistics=class_for_ir_statistics, attribute_id=attribute_id,
            pred_target_column=pred_target_column)

        self.percentage = percentage
        self.preserve_order = preserve_order

    def configure_resultproducer(self):
        """
        Configures and returns the ResultProducer and PropertyPath as tuple.

        :return: producer and property path
        :rtype: tuple
        """
        rproducer = JClass("weka.experiment.RandomSplitResultProducer")()
        rproducer.setRandomizeData(not self.preserve_order)
        rproducer.setTrainPercent(self.percentage)
        speval, classifier = self.configure_splitevaluator()
        rproducer.setSplitEvaluator(speval)
        prop_path = new_array("weka.experiment.PropertyNode", 2)
        cls = JClass("weka.experiment.RandomSplitResultProducer")
        desc = JClass("java.beans.PropertyDescriptor")("splitEvaluator", cls)
        node = JClass("weka.experiment.PropertyNode")(speval, desc, cls)
        prop_path[0] = node
        cls = speval.getClass()
        desc = JClass("java.beans.PropertyDescriptor")("classifier", cls)
        node = JClass("weka.experiment.PropertyNode")(speval.getClass(), desc, cls)
        prop_path[1] = node

        return rproducer, prop_path


class ResultMatrix(OptionHandler):
    """
    For generating results from an Experiment run.
    """

    def __init__(self, classname="weka.experiment.ResultMatrixPlainText", jobject=None, options=None):
        """
        Initializes the specified ResultMatrix using either the classname or the supplied JPype object.

        :param classname: the classname of the ResultMatrix
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
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
        return self.jobject.getRowCount()

    @property
    def columns(self):
        """
        Returns the column count.

        :return: the count
        :rtype: int
        """
        return self.jobject.getColCount()

    def is_col_hidden(self, index):
        """
        Returns whether the column is hidden.

        :param index: the 0-based column index
        :type index: int
        :return: true if hidden
        :rtype: bool
        """
        return self.jobject.getColHidden(index)

    def hide_col(self, index):
        """
        Hides the column.

        :param index: the 0-based column index
        :type index: int
        """
        self.jobject.setColHidden(index, True)

    def show_col(self, index):
        """
        Shows the column.

        :param index: the 0-based column index
        :type index: int
        """
        self.jobject.setColHidden(index, False)

    def is_row_hidden(self, index):
        """
        Returns whether the row is hidden.

        :param index: the 0-based row index
        :type index: int
        :return: true if hidden
        :rtype: bool
        """
        return self.jobject.getRowHidden(index)

    def hide_row(self, index):
        """
        Hides the row.

        :param index: the 0-based row index
        :type index: int
        """
        self.jobject.setRowHidden(index, True)

    def show_row(self, index):
        """
        Shows the row.

        :param index: the 0-based row index
        :type index: int
        """
        self.jobject.setRowHidden(index, False)

    def get_row_name(self, index):
        """
        Returns the row name.

        :param index: the 0-based row index
        :type index: int
        :return: the row name, None if invalid index
        :rtype: str
        """
        return self.jobject.getRowName(index)

    def set_row_name(self, index, name):
        """
        Sets the row name.

        :param index: the 0-based row index
        :type index: int
        :param name: the name of the row
        :type name: str
        """
        self.jobject.setRowName(index, name)

    def get_col_name(self, index):
        """
        Returns the column name.

        :param index: the 0-based row index
        :type index: int
        :return: the column name, None if invalid index
        :rtype: str
        """
        return self.jobject.getColName(index)

    def set_col_name(self, index, name):
        """
        Sets the column name.

        :param index: the 0-based row index
        :type index: int
        :param name: the name of the column
        :type name: str
        """
        self.jobject.setColName(index, name)

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
        return self.jobject.getMean(col, row)

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
        self.jobject.setMean(col, row, mean)

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
        return self.jobject.getStdDev(col, row)

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
        self.jobject.setStdDev(col, row, stdev)

    def average(self, col):
        """
        Returns the average mean at this location (if valid location).

        :param col: the 0-based column index
        :type col: int
        :return: the mean
        :rtype: float
        """
        return self.jobject.getAverage(col)

    def to_string_matrix(self):
        """
        Returns the matrix as a string.

        :return: the generated output
        :rtype: str
        """
        return self.jobject.toStringMatrix()

    def to_string_key(self):
        """
        Returns a key for all the col names, for better readability if the names got cut off.

        :return: the key
        :rtype: str
        """
        return self.jobject.toStringKey()

    def to_string_header(self):
        """
        Returns the header of the matrix as a string.

        :return: the header
        :rtype: str
        """
        return self.jobject.toStringHeader()

    def to_string_summary(self):
        """
        returns the summary as string.

        :return: the summary
        :rtype: str
        """
        return self.jobject.toStringSummary()

    def to_string_ranking(self):
        """
        Returns the ranking in a string representation.

        :return: the ranking
        :rtype: str
        """
        return self.jobject.toStringRanking()


class Tester(OptionHandler):
    """
    For generating statistical results from an experiment.
    """

    def __init__(self, classname="weka.experiment.PairedCorrectedTTester", jobject=None, options=None, swap_rows_and_cols=False):
        """
        Initializes the specified tester using either the classname or the supplied JPype object.

        :param classname: the classname of the tester
        :type classname: str
        :param jobject: the JPype object to use
        :type jobject: JPype object
        :param options: the list of commandline options to set
        :type options: list
        :param swap_rows_and_cols: whether to swap rows/columns, to compare datasets rather than classifiers
        :type swap_rows_and_cols: bool
        """
        if jobject is None:
            jobject = Tester.new_instance(classname)
        self.enforce_type(jobject, "weka.experiment.Tester")
        self.columns_determined = False
        self._run_column = "Key_Run"
        self._fold_column = "Key_Fold"
        self._swap_rows_and_cols = swap_rows_and_cols
        self._dataset_columns = ["Key_Dataset"]
        self._result_columns = ["Key_Scheme", "Key_Scheme_options", "Key_Scheme_version_ID"]
        super(Tester, self).__init__(jobject=jobject, options=options)

    @property
    def swap_rows_and_cols(self):
        """
        Returns whether to swap rows/cols.

        :return: whether to swap
        :rtype: bool
        """
        return self._swap_rows_and_cols

    @swap_rows_and_cols.setter
    def swap_rows_and_cols(self, swap):
        """
        Sets whether to swap rows/cols.

        :param swap: whether to swap
        :type swap: bool
        """
        self.columns_determined = False
        self._swap_rows_and_cols = swap

    @property
    def resultmatrix(self):
        """
        Returns the ResultMatrix instance in use.

        :return: the matrix in use
        :rtype: ResultMatrix
        """
        return ResultMatrix(jobject=self.jobject.getResultMatrix())

    @resultmatrix.setter
    def resultmatrix(self, matrix):
        """
        Sets the ResultMatrix to use.

        :param matrix: the ResultMatrix instance to use
        :type matrix: ResultMatrix
        """
        self.jobject.setResultMatrix(matrix.jobject)

    @property
    def instances(self):
        """
        Returns the data used in the analysis.

        :return: the data in use
        :rtype: Instances
        """
        inst = self.jobject.getInstances()
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
        self.jobject.setInstances(data.jobject)
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

        if self.swap_rows_and_cols:
            dataset_columns = self.result_columns
            result_columns = self.dataset_columns
        else:
            dataset_columns = self.dataset_columns
            result_columns = self.result_columns

        # dataset
        if dataset_columns is None:
            raise Exception("No dataset columns set!")
        cols = ""
        for name in dataset_columns:
            att = data.attribute_by_name(name)
            if att is None:
                raise Exception("Dataset column not found: " + name)
            if len(cols) > 0:
                cols += ","
            cols += str(att.index + 1)
        self.jobject.setDatasetKeyColumns(Range(ranges=cols).jobject)

        # run
        if self.run_column is None:
            raise Exception("No run columnn set!")
        att = data.attribute_by_name(self.run_column)
        if att is None:
            raise Exception("Run column not found: " + self.run_column)
        self.jobject.setRunColumn(att.index)

        # fold
        if not self.fold_column is None:
            att = data.attribute_by_name(self.fold_column)
            if att is None:
                index = -1
            else:
                index = att.index
            self.jobject.setFoldColumn(index)

        # result
        if result_columns is None:
            raise Exception("No result columns set!")
        cols = ""
        for name in result_columns:
            att = data.attribute_by_name(name)
            if att is None:
                raise Exception("Result column not found: " + name)
            if len(cols) > 0:
                cols += ","
            cols += str(att.index + 1)
        self.jobject.setResultsetKeyColumns(Range(ranges=cols).jobject)

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
        return self.jobject.header(comparison_column)

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
        return self.jobject.multiResultsetFull(base_resultset, comparison_column)

    def multi_resultset_ranking(self, comparison_column):
        """
        Creates a ranking.

        :param comparison_column: the 0-based index of the column to compare against
        :type comparison_column: int
        :return: the ranking
        :rtype: str
        """
        return self.jobject.multiResultsetRanking(comparison_column)

    def multi_resultset_summary(self, comparison_column):
        """
        Carries out a comparison between all resultsets, counting the number of datsets where one resultset
        outperforms the other.

        :param comparison_column: the 0-based index of the column to compare against
        :type comparison_column: int
        :return: the summary
        :rtype: str
        """
        return self.jobject.multiResultsetSummary(comparison_column)
