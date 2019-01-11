Examples
========

The following examples are meant to be executed in sequence, as they rely on previous steps,
e.g., on data present.

For more examples, check out the example repository on github:

`github.com/fracpete/python-weka-wrapper3-examples <https://github.com/fracpete/python-weka-wrapper3-examples>`__


Start up JVM
------------

.. code-block:: python

   import weka.core.jvm as jvm
   jvm.start()

For more information, check out the help of the `jvm` module:

.. code-block:: python

   help(jvm.start)
   help(jvm.stop)


Location of the datasets
------------------------

The following examples assume the datasets to be present in the `data_dir` directory. For instance,
this could be the following directory:

.. code-block:: python

   data_dir = "/my/datasets/"


Load dataset and print it
-------------------------

.. code-block:: python

   from weka.core.converters import Loader
   loader = Loader(classname="weka.core.converters.ArffLoader")
   data = loader.load_file(data_dir + "iris.arff")
   data.class_is_last()

   print(data)

The `weka.core.converters` module has a convenience method for loading datasets
called `load_any_file`. This method determines a loader based on the file extension
and then loads the full dataset:

.. code-block:: python

   import weka.core.converters as converters
   data = converters.load_any_file(data_dir + "iris.arff")
   data.class_is_last()

   print(data)


Output help from underlying OptionHandler
-----------------------------------------

If the underlying Java class implements the ``weka.core.OptionHandler`` method, then
you can use the ``to_help()`` method to generate a string containing the ``globalInfo()``
and ``listOptions()`` information:

.. code-block:: python

   from weka.classifiers import Classifier
   cls = Classifier(classname="weka.classifiers.trees.J48")
   print(cls.to_help())


Option handling
---------------

Any class derived from ``OptionHandler`` (module ``weka.core.classes``) allows 
getting and setting of the options via the property ``options``. Depending on
the sub-class, you may also provide the options already when instantiating the
class. The following two examples instantiate a J48 classifier, one using
the ``options`` property and the other using the shortcut through the constructor:

.. code-block:: python

   from weka.classifiers import Classifier
   cls = Classifier(classname="weka.classifiers.trees.J48")
   cls.options = ["-C", "0.3"]

.. code-block:: python

   from weka.classifiers import Classifier
   cls = Classifier(classname="weka.classifiers.trees.J48", options=["-C", "0.3"])

You can use the ``options`` property also to retrieve the currently set options:

.. code-block:: python

   from weka.classifiers import Classifier
   cls = Classifier(classname="weka.classifiers.trees.J48", options=["-C", "0.3"])
   print(cls.options)


Build classifier on dataset, output predictions
-----------------------------------------------

.. code-block:: python

   from weka.classifiers import Classifier
   cls = Classifier(classname="weka.classifiers.trees.J48", options=["-C", "0.3"])
   cls.build_classifier(data)

   for index, inst in enumerate(data):
       pred = cls.classify_instance(inst)
       dist = cls.distribution_for_instance(inst)
       print(str(index+1) + ": label index=" + str(pred) + ", class distribution=" + str(dist))


Build classifier on dataset, print model and draw graph
-------------------------------------------------------

.. code-block:: python

   from weka.classifiers import Classifier
   cls = Classifier(classname="weka.classifiers.trees.J48", options=["-C", "0.3"])
   cls.build_classifier(data)

   print(cls)

   import weka.plot.graph as graph  # NB: pygraphviz and PIL are required
   graph.plot_dot_graph(cls.graph)


Build classifier incrementally with data and print model
--------------------------------------------------------

.. code-block:: python

   loader = Loader(classname="weka.core.converters.ArffLoader")
   iris_inc = loader.load_file(data_dir + "iris.arff", incremental=True)
   iris_inc.class_is_last()

   print(iris_inc)

   cls = Classifier(classname="weka.classifiers.bayes.NaiveBayesUpdateable")
   cls.build_classifier(iris_inc)
   for inst in loader:
       cls.update_classifier(inst)

   print(cls)


Cross-validate filtered classifier and print evaluation and display ROC
-----------------------------------------------------------------------

.. code-block:: python

   data = loader.load_file(data_dir + "diabetes.arff")
   data.class_is_last()

   from weka.filters import Filter
   remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1-3"])

   cls = Classifier(classname="weka.classifiers.bayes.NaiveBayes")

   from weka.classifiers import FilteredClassifier
   fc = FilteredClassifier()
   fc.filter = remove
   fc.classifier = cls

   from weka.classifiers import Evaluation
   from weka.core.classes import Random
   evl = Evaluation(data)
   evl.crossvalidate_model(fc, data, 10, Random(1))

   print(evl.percent_correct)
   print(evl.summary())
   print(evl.class_details())

   import weka.plot.classifiers as plcls  # NB: matplotlib is required
   plcls.plot_roc(evl, class_index=[0, 1], wait=True)


Cross-validate regressor, display classifier errors and predictions
-------------------------------------------------------------------

.. code-block:: python

   from weka.classifiers import PredictionOutput, KernelClassifier, Kernel
   data = loader.load_file(data_dir + "bolts.arff")
   data.class_is_last()

   cls = KernelClassifier(classname="weka.classifiers.functions.SMOreg", options=["-N", "0"])
   kernel = Kernel(classname="weka.classifiers.functions.supportVector.RBFKernel", options=["-G", "0.1"])
   cls.kernel = kernel
   pout = PredictionOutput(classname="weka.classifiers.evaluation.output.prediction.PlainText")
   evl = Evaluation(data)
   evl.crossvalidate_model(cls, data, 10, Random(1), pout)

   print(evl.summary())
   print(pout.buffer_content())

   import weka.plot.classifiers as plcls  # NB: matplotlib is required
   plcls.plot_classifier_errors(evl.predictions, wait=True)


Parameter optimization - GridSearch
-----------------------------------

The following code optimizes the `C` parameter of `SMOreg` and the `gamma` parameter of its `RBFKernel`:

.. code-block:: python

   from weka.classifiers import GridSearch
   grid = GridSearch(options=["-sample-size", "100.0", "-traversal", "ROW-WISE", "-num-slots", "1", "-S", "1"])
   grid.evaluation = "CC"
   grid.y = {"property": "kernel.gamma", "min": -3.0, "max": 3.0, "step": 1.0, "base": 10.0, "expression": "pow(BASE,I)"}
   grid.x = {"property": "C", "min": -3.0, "max": 3.0, "step": 1.0, "base": 10.0, "expression": "pow(BASE,I)"}
   cls = Classifier(
       classname="weka.classifiers.functions.SMOreg",
       options=["-K", "weka.classifiers.functions.supportVector.RBFKernel"])
   grid.classifier = cls
   grid.build_classifier(train)
   print("Model:\n" + str(grid))
   print("\nBest setup:\n" + grid.best.to_commandline())

**NB:** Make sure that the `GridSearch` package is not installed, as the `GridSearch` meta-classifier is already
part of the monolithic `weka.jar` that comes with *python-weka-wrapper3*.


Parameter optimization - MultiSearch
------------------------------------

The following code optimizes the `C` parameter of `SMOreg` and the `gamma` parameter of its `RBFKernel`:

.. code-block:: python

   from weka.core.classes import ListParameter, MathParameter
   multi = MultiSearch(
       options=["-sample-size", "100.0", "-initial-folds", "2", "-subsequent-folds", "2",
                "-num-slots", "1", "-S", "1"])
   multi.evaluation = "CC"
   mparam = MathParameter()
   mparam.prop = "classifier.kernel.gamma"
   mparam.minimum = -3.0
   mparam.maximum = 3.0
   mparam.step = 1.0
   mparam.base = 10.0
   mparam.expression = "pow(BASE,I)"
   lparam = ListParameter()
   lparam.prop = "classifier.C"
   lparam.values = ["-2.0", "-1.0", "0.0", "1.0", "2.0"]
   multi.parameters = [mparam, lparam]
   cls = Classifier(
       classname="weka.classifiers.functions.SMOreg",
       options=["-K", "weka.classifiers.functions.supportVector.RBFKernel"])
   multi.classifier = cls
   multi.build_classifier(train)
   print("Model:\n" + str(multi))
   print("\nBest setup:\n" + multi.best.to_commandline())

**NB:** `multisearch-weka-package <https://github.com/fracpete/multisearch-weka-package>`_ must be installed for
this to work.


Experiments
-----------

.. code-block:: python

   datasets = [
       data_dir + "iris.arff",
       data_dir + "vote.arff",
       data_dir + "anneal.arff"
   ]
   classifiers = [
       Classifier(classname="weka.classifiers.rules.ZeroR"),
       Classifier(classname="weka.classifiers.trees.J48"),
       Classifier(classname="weka.classifiers.trees.REPTree"),
   ]
   result = "exp.arff"
   from weka.experiments import SimpleCrossValidationExperiment
   exp = SimpleCrossValidationExperiment(
       classification=True,
       runs=10,
       folds=10,
       datasets=datasets,
       classifiers=classifiers,
       result=result)
   exp.setup()
   exp.run()

   import weka.core.converters
   loader = weka.core.converters.loader_for_file(result)
   data = loader.load_file(result)
   from weka.experiments import Tester, ResultMatrix
   matrix = ResultMatrix(classname="weka.experiment.ResultMatrixPlainText")
   tester = Tester(classname="weka.experiment.PairedCorrectedTTester")
   tester.resultmatrix = matrix
   comparison_col = data.attribute_by_name("Percent_correct").index
   tester.instances = data

   print(tester.header(comparison_col))
   print(tester.multi_resultset_full(0, comparison_col))
   print(tester.multi_resultset_full(1, comparison_col))


Clustering
----------

.. code-block:: python

   data = loader.load_file(data_dir + "vote.arff")
   data.delete_last_attribute()

   from weka.clusterers import Clusterer
   clusterer = Clusterer(classname="weka.clusterers.SimpleKMeans", options=["-N", "3"])
   clusterer.build_clusterer(data)

   print(clusterer)

   # cluster the data
   for inst in data:
       cl = clusterer.cluster_instance(inst)  # 0-based cluster index
       dist = clusterer.distribution_for_instance(inst)   # cluster membership distribution
       print("cluster=" + str(cl) + ", distribution=" + str(dist))


Associations
------------

.. code-block:: python

   data = loader.load_file(data_dir + "vote.arff")
   data.class_is_last()

   from weka.associations import Associator
   associator = Associator(classname="weka.associations.Apriori", options=["-N", "9", "-I"])
   associator.build_associations(data)

   print(associator)


Attribute selection
-------------------

.. code-block:: python

   data = loader.load_file(data_dir + "vote.arff")
   data.class_is_last()

   from weka.attribute_selection import ASSearch, ASEvaluation, AttributeSelection
   search = ASSearch(classname="weka.attributeSelection.BestFirst", options=["-D", "1", "-N", "5"])
   evaluator = ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval", options=["-P", "1", "-E", "1"])
   attsel = AttributeSelection()
   attsel.search(search)
   attsel.evaluator(evaluator)
   attsel.select_attributes(data)

   print("# attributes: " + str(attsel.number_attributes_selected))
   print("attributes: " + str(attsel.selected_attributes))
   print("result string:\n" + attsel.results_string)


Data generators
---------------

.. code-block:: python

   from weka.datagenerators import DataGenerator
   generator = DataGenerator(classname="weka.datagenerators.classifiers.classification.Agrawal", options=["-B", "-P", "0.05"])
   DataGenerator.make_data(generator, ["-o", data_dir + "generated.arff"])

   generator = DataGenerator(classname="weka.datagenerators.classifiers.classification.Agrawal", options=["-n", "10", "-r", "agrawal"])
   generator.dataset_format = generator.define_data_format()
   print(generator.dataset_format)
   if generator.single_mode_flag:
       for i in range(generator.num_examples_act):
           print(generator.generate_example())
   else:
       print(generator.generate_examples())


Filters
-------

.. code-block:: python

   data = loader.load_file(data_dir + "vote.arff")

   from weka.filters import Filter
   remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "last"])
   remove.inputformat(data)
   filtered = remove.filter(data)

   print(filtered)


Partial classnames
------------------

All classes derived from `weka.core.classes.JavaObject` like `Classifier`, `Filter`, etc.,
allow the use of partial classnames. So instead of instantiating a classifier like this:

.. code-block:: python

   cls = Classifier(classname="weka.classifiers.trees.J48", options=["-C", "0.3"])

You can instantiate it with a shortened classname (must start with a `.`):

.. code-block:: python

   cls = Classifier(classname=".J48", options=["-C", "0.3"])

**NB:** This will fail with an exception if there are no or multiple matches.
For instance, the following will result in an error, as there are two `Discretize`
filters, supervised and unsupervised:

.. code-block:: python

   cls = Filter(classname=".Discretize")

.. code-block:: bash

   Exception: Found multiple matches for '.Discretize':
   weka.filters.supervised.attribute.Discretize
   weka.filters.unsupervised.attribute.Discretize


Packages
--------

The following examples show how to list, install and uninstall an *official* package:

.. code-block:: python

   import weka.core.packages as packages
   items = packages.all_packages()
   for item in items:
       if item.get_name() == "CLOPE":
           print(item.name + " " + item.url)

   packages.install_package("CLOPE")
   items = packages.installed_packages()
   for item in items:
       print(item.name + " " + item.url)

   packages.uninstall_package("CLOPE")
   items = packages.installed_packages()
   for item in items:
       print(item.name + " " + item.url)

You can also install *unofficial* packages. The following example installs a previously downloaded zip file:

.. code-block:: python

   import weka.core.packages as packages
   packages.install_package("/some/where/funky-package-1.0.0.zip")

And here installing it directly from a URL:

.. code-block:: python

   import weka.core.packages as packages
   packages.install_package("http://some.server.com/funky-package-1.0.0.zip")


Stop JVM
--------

.. code-block:: python

   jvm.stop()


Database access
---------------

Thanks to JDBC (Java Database Connectivity) it is very easy to connect to SQL databases and load data
as an Instances object. However, since we rely on 3rd-party libraries to achieve this, we need to
specify the database JDBC driver jar when we are starting up the JVM. For instance, adding a MySQL
driver called `mysql-connector-java-X.Y.Z-bin.jar`:

.. code-block:: python

   jvm.start(class_path=["/some/where/mysql-connector-java-X.Y.Z-bin.jar"])

Assuming the following parameters:

 * database host is `dbserver`
 * database is called `mydb`
 * database user is `me`
 * database password is `verysecret`

We can use the following code to select all the data from table `lotsadata`.

.. code-block:: python

   from weka.core.database import InstanceQuery
   iquery = InstanceQuery()
   iquery.db_url = "jdbc:mysql://dbserver:3306/mydb"
   iquery.user = "me"
   iquery.password = "verysecret"
   iquery.query = "select * from lotsadata"
   data = iquery.retrieve_instances()
