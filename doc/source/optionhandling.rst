Option handling
===============

Most algorithms in Weka support option handling with access through string arrays
(in Python string lists). As long as there are only a few possible options, this
is fine. However, once there are nested algorithms with their own options involved,
like a support vector machine with its nested kernel, then this can get a bit
convoluted.

In order to make life a bit easier with all those options, the `weka.core.classes`
module comes with support for splitting, joining and generating code from options.


Splitting
---------

The `-action split` option allows you to split an option string that is enclosed
in double quotes:

.. code-block:: bash

   weka.core.classes -action split "weka.classifiers.meta.FilteredClassifier -F \"weka.filters.unsupervised.attribute.RemoveType -T string\" -W weka.classifiers.functions.SMO -- -C 1.0 -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 -K \"weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007\""

It generates Python code that initializes a list of strings:

.. code-block:: python

   options = [
       "weka.classifiers.meta.FilteredClassifier",
       "-F",
       "weka.filters.unsupervised.attribute.RemoveType -T string",
       "-W",
       "weka.classifiers.functions.SMO",
       "--",
       "-C",
       "1.0",
       "-L",
       "0.001",
       "-P",
       "1.0E-12",
       "-N",
       "0",
       "-V",
       "-1",
       "-W",
       "1",
       "-K",
       "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007"]


Joining
-------

In order to generate a correctly double-quoted command-line string from a configuration
obtained, e.g., from the Weka Explorer, you can use the `-action join` option:

.. code-block:: bash

   weka.core.class -action join weka.classifiers.meta.FilteredClassifier -F "weka.filters.unsupervised.attribute.RemoveType -T string" -W weka.classifiers.functions.SMO -- -C 1.0 -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 -K "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007"

This generates the following Python code:

.. code-block:: python

   cmdline = "weka.classifiers.meta.FilteredClassifier -F \"weka.filters.unsupervised.attribute.RemoveType -T string\" -W weka.classifiers.functions.SMO -- -C 1.0 -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 -K \"weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007\""


Code
----

If you want to create Python code that instantiates the class and sets its options, then
you can use the `-action code` option:

.. code-block:: bash

   weka.core.class -action code weka.classifiers.meta.FilteredClassifier -F "weka.filters.unsupervised.attribute.RemoveType -T string" -W weka.classifiers.functions.SMO -- -C 1.0 -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 -K "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007"

This generates the following code, instantiating an `OptionHandler` object
and setting its options:

.. code-block:: python

   options = [
       "-F",
       "weka.filters.unsupervised.attribute.RemoveType -T string",
       "-W",
       "weka.classifiers.functions.SMO",
       "--",
       "-C",
       "1.0",
       "-L",
       "0.001",
       "-P",
       "1.0E-12",
       "-N",
       "0",
       "-V",
       "-1",
       "-W",
       "1",
       "-K",
       "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007"]
   handler = OptionHandler(JavaObject.new_instance("weka.classifiers.meta.FilteredClassifier"))
   handler.options = options
