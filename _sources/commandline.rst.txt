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


Command-line help screen:

::

    usage: pww-datagenerator [-h] [-j classpath] [-X heap] datagenerator ...

    Executes a data generator from the command-line. Calls JVM start/stop
    automatically.

    positional arguments:
      datagenerator  data generator classname, e.g.,
                     weka.datagenerators.classifiers.classification.LED24
      option         additional data generator options

    optional arguments:
      -h, --help     show this help message and exit
      -j classpath   additional classpath, jars/directories
      -X heap        max heap size for jvm, e.g., 512m



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


Command-line help screen:

::

    usage: pww-filter [-h] [-j classpath] [-X heap] -i input1 -o output1
                      [-r input2] [-s output2] [-c classindex]
                      filter ...

    Executes a filter from the command-line. Calls JVM start/stop automatically.

    positional arguments:
      filter         filter classname, e.g., weka.filters.AllFilter
      option         additional filter options

    optional arguments:
      -h, --help     show this help message and exit
      -j classpath   additional classpath, jars/directories
      -X heap        max heap size for jvm, e.g., 512m
      -i input1      input file 1
      -o output1     output file 1
      -r input2      input file 2
      -s output2     output file 2
      -c classindex  1-based class attribute index



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


Command-line help screen:

::

    usage: pww-classifier [-h] [-j classpath] [-X heap] -t train [-T test]
                          [-c class index] [-d outmodel] [-l inmodel]
                          [-x num folds] [-s seed] [-v] [-o] [-i] [-k]
                          [-m costmatrix] [-g graph]
                          classifier ...

    Performs classification/regression from the command-line. Calls JVM start/stop
    automatically.

    positional arguments:
      classifier      classifier classname, e.g., weka.classifiers.trees.J48
      option          additional classifier options

    optional arguments:
      -h, --help      show this help message and exit
      -j classpath    additional classpath, jars/directories
      -X heap         max heap size for jvm, e.g., 512m
      -t train        Training set file
      -T test         Test set file
      -c class index  1-based class attribute index
      -d outmodel     model output file name
      -l inmodel      model input file name
      -x num folds    number of folds for cross-validation
      -s seed         seed value for randomization
      -v              no statistics for training
      -o              only statistics, don't output model
      -i              output information retrieval statistics
      -k              output information theoretic statistics
      -m costmatrix   cost matrix file
      -g graph        output file for graph (if supported)


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


Command-line help screen:

::

    usage: pww-clusterer [-h] [-j classpath] [-X heap] -t train [-T test]
                         [-d outmodel] [-l inmodel] [-p attributes] [-x num folds]
                         [-s seed] [-c class index] [-g graph]
                         clusterer ...

    Performs clustering from the command-line. Calls JVM start/stop automatically.

    positional arguments:
      clusterer       clusterer classname, e.g., weka.clusterers.SimpleKMeans
      option          additional clusterer options

    optional arguments:
      -h, --help      show this help message and exit
      -j classpath    additional classpath, jars/directories
      -X heap         max heap size for jvm, e.g., 512m
      -t train        training set file
      -T test         test set file
      -d outmodel     model output file name
      -l inmodel      model input file name
      -p attributes   attribute range
      -x num folds    number of folds
      -s seed         seed value for randomization
      -c class index  1-based class attribute index
      -g graph        graph output file (if supported)


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


Command-line help screen:

::

    usage: pww-attsel [-h] [-j classpath] [-X heap] -i input [-c class index]
                      [-s search] [-x num folds] [-n seed]
                      evaluator ...

    Performs attribute selection from the command-line. Calls JVM start/stop
    automatically.

    positional arguments:
      evaluator       evaluator classname, e.g.,
                      weka.attributeSelection.CfsSubsetEval
      option          additional evaluator options

    optional arguments:
      -h, --help      show this help message and exit
      -j classpath    additional classpath, jars/directories
      -X heap         max heap size for jvm, e.g., 512m
      -i input        input file
      -c class index  1-based class attribute index
      -s search       search method, classname and options
      -x num folds    number of folds
      -n seed         the seed value for randomization


Associators
-----------

Associators, like `Apriori`, can be run like this:

.. code-block:: bash

   pww-associator \
       -t /my/datasets/iris.arff \
       weka.associations.Apriori \
       -N 9 -I


Command-line help screen:

::

    usage: pww-associator [-h] [-j classpath] [-X heap] -t train associator ...

    Executes an associator from the command-line. Calls JVM start/stop
    automatically.

    positional arguments:
      associator    associator classname, e.g., weka.associations.Apriori
      option        additional associator options

    optional arguments:
      -h, --help    show this help message and exit
      -j classpath  additional classpath, jars/directories
      -X heap       max heap size for jvm, e.g., 512m
      -t train      training set file


Package management
------------------

Versions newer than 0.2.9 also offer package management from the command-line via the `pww-packages`
command. There are several sub-commands available:

::

    usage: pww-packages [-h]
                       {list,info,install,uninstall,remove,suggest,is-installed}
                       ...

    Manages Weka packages.

    positional arguments:
      {list,info,install,uninstall,remove,suggest,is-installed}
        list                For listing all/installed/available packages
        info                Outputs information about packages
        install             For installing one or more packages
        uninstall (remove)  For uninstalling one or more packages
        suggest             For suggesting packages that contain the specified
                            class
        is-installed        Checks whether a package is installed, simply outputs
                            true/false

    optional arguments:
      -h, --help            show this help message and exit


Listing packages
++++++++++++++++

Listing all, available or installed packages can be done using the `list` sub-command:

::

    usage: pww-packages list [-h] [-f {text,json}] [-o FILE] [-r]
                             [{all,installed,available}]

    positional arguments:
      {all,installed,available}
                            defines what packages to list

    optional arguments:
      -h, --help            show this help message and exit
      -f {text,json}, --format {text,json}
                            the output format to use
      -o FILE, --output FILE
                            the file to store the output in, uses stdout if not
                            supplied
      -r, --refresh-cache   whether to refresh the package cache


Info on packages
++++++++++++++++

Outputting information on one or more packages is achieved with the `list` sub-command:

::

    usage: pww-packages info [-h] [-t {brief,full}] [-f {text,json}] [-o FILE]
                             [-r]
                             name [name ...]

    positional arguments:
      name                  the package(s) to output the information for

    optional arguments:
      -h, --help            show this help message and exit
      -t {brief,full}, --type {brief,full}
                            the type of information to output
      -f {text,json}, --format {text,json}
                            the output format to use
      -o FILE, --output FILE
                            the file to store the output in, uses stdout if not
                            supplied
      -r, --refresh-cache   whether to refresh the package cache



Installing/uninstalling/check installed status
++++++++++++++++++++++++++++++++++++++++++++++

The `install` sub-command installs one or more packages:

::

    usage: pww-packages install [-h] packages [packages ...]

    positional arguments:
      packages    the name of the package(s) to install, append '==VERSION' to pin
                  to a specific version

    optional arguments:
      -h, --help  show this help message and exit


The `uninstall` (or `remove`) sub-command removes one or more packages:

::

    usage: pww-packages uninstall [-h] packages [packages ...]

    positional arguments:
      packages    the name of the package(s) to uninstall

    optional arguments:
      -h, --help  show this help message and exit


The `is-installed` sub-command outputs whether a package is installed or not:

::

    usage: pww-packages is-installed [-h] [-f {text,json}] [-o FILE]
                                     name [name ...]

    positional arguments:
      name                  the name of the package to check, append '==VERSION'
                            to pin to a specific version

    optional arguments:
      -h, --help            show this help message and exit
      -f {text,json}, --format {text,json}
                            the output format to use
      -o FILE, --output FILE
                            the file to store the output in, uses stdout if not
                            supplied



Suggest packages
++++++++++++++++

If you are not sure which package a certain class is part of, then use the `suggest`
sub-command to help with that (this works only for official packages):

::

    usage: pww-packages suggest [-h] [-e] [-f {text,json}] [-o FILE] classname

    positional arguments:
      classname             the classname to suggest packages for

    optional arguments:
      -h, --help            show this help message and exit
      -e, --exact           whether to match the name exactly or perform substring
                            matching
      -f {text,json}, --format {text,json}
                            the output format to use
      -o FILE, --output FILE
                            the file to store the output in, uses stdout if not
                            supplied

