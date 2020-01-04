Changelog
=========

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



