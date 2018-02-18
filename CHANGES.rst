Changelog
=========

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



