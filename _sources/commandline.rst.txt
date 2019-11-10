Command-line
============

From command-line, *python-weka-wrapper* behaves similar to Weka itself, i.e., the command-line.
Most of the general options are available, as well as the following:

* `-j` for adding additional jars, in the same format as the classpath for the platform.
  E.g., for Linux, `-j /some/where/a.jar:/other/place/b.jar`
* `-X` for defining the maximum heap size.
  E.g., `-X 512m` for 512 MB of heap size.

The following examples are all for a Linux bash environment. Windows users have to replace
forwarding slashes `/` with backslashes `\\` and place the command on a single line with the
backslashes `\\` at the end of the lines removed.


Data generators
---------------

Artifical data can be generated using one of Weka's data generators, e.g., the
`Agrawal` classification generator:

.. code-block:: bash

   pww-datagenerator \
       -o /tmp/out.arff \
       weka.datagenerators.classifiers.classification.Agrawal


Filters
-------

Filtering a single ARFF dataset, removing the last attribute using the `Remove` filter:

.. code-block:: bash

   pww-filter \
       -i /my/datasets/iris.arff \
       -o /tmp/out.arff \
       -c last \
       weka.filters.unsupervised.attribute.Remove \
       -R last

For batch filtering, you can use the `-r` and `-s` options for the input and output
for the second file.


Classifiers
-----------

Example on how to cross-validate a `J48` classifier (with confidence factor 0.3)
on the iris UCI dataset:

.. code-block:: bash

   pww-classifier \
        -t /my/datasets/iris.arff \
        -c last \
        weka.classifiers.trees.J48
        -C 0.3


Clusterers
----------

Example on how to perform classes-to-clusters evaluation for `SimpleKMeans`
(with 3 clusters) using the iris UCI dataset:

.. code-block:: bash

   pww-clusterer \
       -t /my/datasets/iris.arff \
       -c last \
       weka.clusterers.SimpleKMeans
       -N 3


Attribute selection
-------------------

You can perform attribute selection using `BestFirst` as search algorithm and
`CfsSubsetEval` as evaluator as follows:

.. code-block:: bash

   pww-attsel \
       -i /my/datasets/iris.arff \
       -x 5 \
       -n 42 \
       -s "weka.attributeSelection.BestFirst -D 1 -N 5"
       weka.attributeSelection.CfsSubsetEval \
       -P 1 \
       -E 1


Associators
-----------

Associators, like `Apriori`, can be run like this:

.. code-block:: bash

   pww-associator \
       -t /my/datasets/iris.arff \
       weka.associations.Apriori \
       -N 9 -I
