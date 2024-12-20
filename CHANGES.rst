Changelog
=========

0.3.3 (????-??-??)
------------------

- switched to underscores in project name


0.3.2 (2024-08-05)
------------------

- improved logging output in command-line scripts (eg pww-classifier)
- added sub-command `freeze` to the `pww-packages` command-line tool to output the
  currently installed packages in pip-like format (unofficial packages get URL appended)
  either to stdout or to text file (eg `requirements.txt`)
- the sub-command `install` of the `pww-packages` command-line tool can process
  a requirements text file now as well
- added `pww_version()` function to `weka.core.version` to obtain the installed
  version of python-weka-wrapper3
- added `with_graph_support()` function to `weka.core.version` to see whether
  python-weka-wrapper3 has support for graphs using pygraphviz
- added `with_plot_support()` function to `weka.core.version` to see whether
  python-weka-wrapper3 has plotting support via matplotlib
- added sub-command `bootstrap` to the `pww-packages` command-line tool to output a
  Python script that can reinstall python-weka-wrapper3 and all the packages in
  another virtual environment or even another machine
- added `is_official_package` function to `weka.core.packages` module to check
  whether a package is an official one from the Weka package repository or not


0.3.1 (2024-07-17)
------------------

- the `max_heap_size` parameter of the `start` method from the `weka.core.jvm` module now has an effect


0.3.0 (2024-07-12)
------------------

- added `is_additional_measure_producer` variable, `additional_measures` property and
  `additional_measure(str)` method to the `weka.classifiers.Classifier` class,
  giving convenient access to classes implementing `weka.core.AdditionalMeasureProducer`
- replaced javabridge with jpype behind the scenes, simplifying native API calls
- removed property `JavaObject.jclasswrapper`
- property `JavaObject.jwrapper` is now deprecated and `JavaObject.jobject` should be used instead
- renamed `JavaArray.new_instance` to `JavaArray.new_array`
- now works on M1/M2 Macs
- updated doc strings
- updated documentation, especially around installation


0.2.16 (2024-05-10)
-------------------

- `setup.py` no longer lists python-javabridge with github URL, as it fails to
  install via pip otherwise


0.2.15 (2024-05-10)
-------------------

- the methods `create_instances_from_lists` and `create_instances_from_matrices` of the
  `weka.core.dataset` module can handle missing values now (`None` in case of lists,
  `nan` in case of matrices), as well as being able to force columns to be nominal
- added the method `load_csv_file` to the module `weka.core.converters` to provide a more
  reliable way of loading CSV files compared to Weka's native `CSVLoader` converter
  (uses Python's csv module and then calls `create_instances_from_lists`).
- added `simple_range` library as dependency to make it easier to generate integer list from range strings
- added `weka.core.utils` module with following methods: correlation, variance, normalize
- updated requirements (and install instructions) to make pww3 work with Python 3.11+


0.2.14 (2023-07-04)
-------------------

- extracted arpack_combined.jar, core.jar and mtj.jar from weka.jar to make them available under Java 17


0.2.13 (2023-04-26)
-------------------

- moved `Configurable` and `JSONObject` into *configurable-objects* library
- moved base flow components into *simple-data-flow* library
- added methods `subset_results`, `rank_results` to class `AttributeSelection`
  (module: `weka.attribute_selection`) to give access to cross-validation
  output in numeric rather textual form (NB: it has to parse the textual CV output).
- made the `plot_experiments` method (module `weka.plot.experiments`) more customizable


0.2.12 (2022-12-08)
-------------------

- method `install_packages` (module: `weka.core.packages`) now no longer interprets
  the installation message returned when installing from URL or local zip file as
  failure to install; also outputs any installation message now in the console;
  now has flags for `fail_fast` mode (first package that fails stops installation process)
  and whether to return `details` (dict per package rather than just a bool for all packages)
- method `install_package` (module: `weka.core.packages`) can return either a
  boolean flag of success or detailed information


0.2.11 (2022-10-11)
-------------------

- methods `install_packages` and `install_missing_packages` of module `weka.core.packages` now
  allow a list of package names instead of tuples (name, version), assuming `latest` as version
- method `get_jclass` in module `weka.core.classes` can handle primitive classes now as well
  (eg `int` -> `java.lang.Integer.TYPE`)
- methods `get_non_public_field` and `call_non_public_method` in module `weka.core.classes`
  allow accessing private/protected fields and calling private/protected methods of Java objects,
  which avoids having to sub-class classes to get public access to them (NB: only works as long
  as the security manager allows that)
- added `split_commandline` method to module `weka.core.classes`, which splits a command-line
  into classname and option list tuple
- the `Instances` class (module: `weka.core.dataset`) now supports slicing
- added methods `plot_xmlbif_graph` and `xmlbif_to_dot` to module `weka.plot.graph` for plotting
  XML BIF graphs generated by BayesNet using GraphViz
- added method `plot_graph` to module `weka.plot.graph` to plot dot or XML BIF graphs


0.2.10 (2022-06-27)
-------------------

- added `logging_level` parameter to the `start` method of the `weka.core.jvm` module, enabling the user
  to turn off debugging output in an easy way (https://github.com/fracpete/python-weka-wrapper3/issues/40)
- added method `cv_splits` to class `Instances` from module `weka.core.dataset` to return a list of
  train/test tuples as used by cross-validation
- the `Tester` class (module: `weka.experiments`) now has an option to swap columns/rows for comparing
  datasets rather than classifiers
- the `SimpleExperiment` class and derived classes (module: `weka.experiments`) now have the additional
  parameters in the constructor: class_for_ir_statistics, attribute_id, pred_target_column
- the method `is_installed` (module: `weka.core.packages`) now can check whether a specific version is installed
- added `pww-packages` entry point to allow managing of Weka packges from the command-line
  (actions: list/info/install/uninstall/suggest/is-installed)


0.2.9 (2022-04-17)
------------------

- method `JavaObject.new_instance` in module `weka.core.classes` now automatically
  installs packages based on suggestions if the JVM was started with the `auto_install`
  flag enabled.
- method `test_model_once` of class `Evaluation` (module: `weka.classifiers`) now has the
  additional parameter `store`, which  allows the recording of the predictions (necessary
  for statistics like AUC)


0.2.8 (2022-03-24)
------------------

- methods `create_instances_from_lists` and `create_instances_from_matrices`
  (module `weka.core.dataset`) now allow the specification of column names,
  for input and output variables.


0.2.7 (2022-02-22)
------------------

- Added property for attribute indices to `DistanceFunction` class (module `weka.core.distances`)
  (thanks to Martin Trat, https://github.com/fracpete/python-weka-wrapper3/pull/39)
- improved instantiation of classes, avoiding misleading output of exceptions
- `JavaArray` class (module: `weka.core.classes`) now has `__str__` and `__repr__` methods that output
  classname and size


0.2.6 (2022-02-01)
------------------

- upgraded bundled Weka to 3.9.6


0.2.5 (2021-12-17)
------------------

- switched to `python-javabridge`, the new name (fork?) of the `javabridge` library
- `Package.__str__` (`weka.core.packages` module) method now returns a string rather than printing the name/version
- added `to_numpy(...)` methods to `Instance` and `Instances` classes (module `weka.core.dataset`)
  to make it easy to obtain a numpy array from the Weka dataset


0.2.4 (2021-11-25)
------------------

- added method `help_for` to `weka.core.classes` module to generate a help screen for an `weka.core.OptionHandler`
  class using just the classname.
- the `to_help` method of the `weka.core.classes.OptionHandler` class now allows to tweak the generated output a
  bit better (e.g., what sections to output).
- setting window title of Matplotlib is now dependent on version (to avoid deprecation notice being output)
- `plot_classifier_errors` (module `weka.plot.classifiers`) now plots the diagonal after adding all the plot data to
  get the right limits


0.2.3 (2021-06-09)
------------------

- added `weka.core.distances` module for distance functions, with `DistanceFunction` base class
- added `avg_silhouette_coefficient` method to `weka.clusterers` to calculate the average silhouette coefficient


0.2.2 (2021-04-23)
------------------

- the `Package` class of the `weka.core.packages` module now has a `version` property to quickly access the version
  which is stored in the meta-data; the `metadata` property now returns a proper Python dictionary
- added convenience methods to the `weka.core.packages` module: `install_packages` to install more than one package,
  `install_missing_package` and `install_missing_packages` to install one or more packages if missing
  (can automatically stop the JVM and exit the process), `uninstall_packages` to remove more than one package in
  one operation


0.2.1 (2021-04-12)
------------------

- the `ASEvaluation` class in the `weka.attribute_selection` module now offers the following methods
  for attribute transformers like PCA: `transformed_header`, `transformed_data`, `convert_instance`
- classes derived from `weka.core.classes.JavaObject` are now serializable via pickle
- added the method `copy_structure` to the `weka.core.dataset.Instances` class to quickly
  get the header of a dataset
- added the property `header` to the following classes that returns the training data structure:
  `ASEvaluation`, `ASSearch`, `Associator`, `Classifier`, `Clusterer`, `TSForecaster`
- methods from `weka.core.serialization` have been moved into `weka.core.classes`, with the
  following methods getting the `serialization_` prefix: `write`, `write_all`, `read`, `read_all`


0.2.0 (2021-02-21)
------------------

- `classes.new_instance` method can take an options list now as well
- added `classes.get_enum` method to return the instance of a Java enum item
- added `classes.new_instance` method to create new instance of Java class
- added `typeconv.jstring_list_to_string_list` method to convert a `java.util.List` containing strings into a Python list
- added `typeconv.jdouble_to_float` method to convert a `java.lang.Double` to a Python float
- in module `typeconv` renamed methods: `string_array_to_list` to `jstring_array_to_list`,
  `string_list_to_array` to `string_list_to_jarray`, `double_matrix_to_ndarray` to `jdouble_matrix_to_ndarray`,
  `enumeration_to_list` to `jenumeration_to_list`, `double_to_float` to `float_to_jfloat`
- added `weka.timeseries` module that wraps the `timeseriesForecasting` Weka package


0.1.16 (2020-12-26)
-------------------

- upgraded Weka to 3.9.5


0.1.15 (2020-10-25)
-------------------

- added `weka.core.systeminfo` module for obtaining output from `weka.core.SystemInfo`
- added `system_info` parameter to `weka.core.jvm.start()` method
- merged PR #33 (https://github.com/fracpete/python-weka-wrapper3/pull/33) to better handle
  associator output


0.1.14 (2020-05-26)
-------------------

- added `AttributeSelectedClassifier` meta-classifier to module `weka.classifiers`
- added `AttributeSelection` meta-filter to module `weka.filters`


0.1.13 (2020-05-06)
-------------------

- added `class_index` parameter to `weka.core.converters.load_any_file`
  and `weka.core.converters.Loader.load_file`, which allows specifying of
  index while loading it (`first`, `second`, `third`, `last-2`, `last-1`,
  `last` or 1-based index).
- added `append` and `clear` methods to `weka.filters.MultiFilter` and
  `weka.classifiers.MultipleClassifiersCombiner` to make adding of
  filters/classifiers easier.
- added `attribute_names()` method to `weka.core.dataset.Instances` class
- added `subset` method to `weka.core.dataset.Instances` class, which returns
  a subset of columns and/or rows.


0.1.12 (2020-01-10)
-------------------

- added method `list_property_names` to `weka.core.classes` module to allow listing of Bean property names
  (which are used by `GridSearch` and `MultiSearch`) for a Java object.


0.1.11 (2020-01-04)
-------------------

- Upgraded Weka to 3.9.4
- added method `suggest_package` to the `weka.core.packages` module for suggesting packages for partial class
  names/package names (`NNge` or `.ft.`) or exact class names (`weka.classifiers.meta.StackingC`)
- the `JavaObject.new_instance` method now suggests packages (if possible) in case the instantiation fails
  due to package not installed or JVM not started with package support


0.1.10 (2019-12-02)
-------------------

- method `train_test_split` of the `weka.dataset.Instances` class now creates a copy of itself before
  applying randomization, to avoid changing the order of data for subsequent calls.


0.1.9 (2019-11-19)
------------------

- method `create_instances_from_matrices` from module `weka.core.dataset` now works with pure numeric data again
- added sections for creating datasets (manual, lists, matrices) to examples documentation


0.1.8 (2019-11-11)
------------------

- added console scripts: `pww-associator`, `pww-attsel`, `pww-classifier`, `pww-clusterer`, `pww-datagenerator`, `pww-filter`
- added `serialize`, `deserialize` methods to `weka.classifiers.Classifier` to simplify loading/saving model
- added `serialize`, `deserialize` methods to `weka.clusterers.Clusterer` to simplify loading/saving model
- added `serialize`, `deserialize` methods to `weka.filters.Filter` to simplify loading/saving filter
- added methods `plot_rocs` and `plot_prcs` to `weka.plot.classifiers` module to plot ROC/PRC curve on same dataset
  for multiple classifiers
- method `plot_classifier_errors` of `weka.plot.classifiers` module now allows plotting predictions of multiple
  classifiers by providing a dictionary
- method `create_instances_from_matrices` from module `weka.core.dataset` now allows string and bytes as well
- method `create_instances_from_lists` from module `weka.core.dataset` now allows string and bytes as well


0.1.7 (2019-01-11)
------------------

- added wrapper classes for association classes that implement `AssociationRuleProducer`
  (package `weka.associations`): `AssociationRules`, `AssociationRule`, `item`
- added `to_source` method to `weka.classifiers.Classifier` and `weka.filters.Filter`
  (underlying Java classes must implement the respective `Sourcable` interface)


0.1.6 (2018-10-28)
------------------

- fixed logging setup in `weka.core.jvm` to avoid global setting global logging
  setup to `DEBUG` (thanks to https://github.com/Arnie97)


0.1.5 (2018-09-16)
------------------

- upgraded to Weka 3.9.3
- `weka.jar` now included in PyPi package
- exposed the following methods in `weka.classifiers.Evaluation`:
  `cumulative_margin_distribution`, `sf_prior_entropy`, `sf_scheme_entropy`


0.1.4 (2018-02-18)
------------------

- upgraded to Weka 3.9.2
- properly initializing package support now, rather than adding package jars to classpath
- added `weka.core.ClassHelper` Java class for obtaining classes and static fields, as
  javabridge only uses the system class loader


0.1.3 (2017-08-23)
------------------

- added `check_for_modified_class_attribute` method to `FilterClassifier` class
- added `complete_classname` method to `weka.core.classes` module, which allows
  completion of partial classnames like `.J48` to `weka.classifiers.trees.J48`
  if there is a unique match; `JavaObject.new_instance` and `JavaObject.check_type`
  now make use of this functionality, allowing for instantiations like
  `Classifier(cls=".J48")`
- `jvm.start(system_cp=True)` no longer fails with a `KeyError: 'CLASSPATH'` if
  there is no `CLASSPATH` environment variable defined
- Libraries `mtl.jar`, `core.jar` and `arpack_combined_all.jar` were added as is
  to the `weka.jar` in the 3.9.1 release instead of adding their content to it.
  Repackaged `weka.jar` to fix this issue (https://github.com/fracpete/python-weka-wrapper3/issues/5)


0.1.2 (2017-01-04)
------------------

- `typeconv.double_matrix_to_ndarray` no longer assumes a square matrix
  (https://github.com/fracpete/python-weka-wrapper3/issues/4)
- `len(Instances)` now returns the number of rows in the dataset (module `weka.core.dataset`)
- added method `insert_attribute` to the `Instances` class
- added class method `create_relational` to the `Attribute` class
- upgraded Weka to 3.9.1


0.1.1 (2016-10-19)
------------------

- `plot_learning_curve` method of module `weka.plot.classifiers` now accepts a list of test sets;
  `*` is index of test set in label template string
- added `missing_value()` methods to `weka.core.dataset` module and `Instance` class
- output variable `y` for convenience method `create_instances_from_lists` in module
  `weka.core.dataset` is now optional
- added convenience method `create_instances_from_matrices` to `weka.core.dataset` module to easily create
  an `Instances` object from numpy matrices (x and y)


0.1.0 (2016-05-09)
------------------

- initial release of Python3 port



