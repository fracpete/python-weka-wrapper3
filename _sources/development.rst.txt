Development
===========

Originally, the Python code of the *python-weka-wrapper3* library shielded the user from the
complicated Java Native Interface (JNI) calls that are required to communicate
with objects in the Java Virtual Machine (JVM). After migrating from python-javabridge to
jpype, this is no longer the case. But thanks to wrapper methods, the underlying calls could change
without affecting any code written by the user, as long as no low-level access was used, such
as using the `jwrapper` or `jclass` properties. Also, the wrapper methods made the code look
more pythonic rather than Java-like.


Calling methods
---------------

Non-static methods
++++++++++++++++++

For calling a **non-static method**, you can simply use the `jobject` property, since jpype
will have added the Java methods.

Here is a code snippet that calls the `buildClassifier` method of a `weka.classifiers.Classifier`
object:

.. code-block:: python

   self.jobject.buildClassifier(data.jobject)


Notes:

* `self.jobject` - the jpype object representing the classifier Java object
* `buildClassifier` - the method that we want to call
* `data.object` - the jpype object representing a `weka.core.Instances` object


Static methods
++++++++++++++

For calling a **static method**, you can surround a class in a `jpype.JClass` wrapper, which will
automatically add access to static methods.
Below is an example for calling the `makeCopy` method of the `weka.classifiers.AbstractClassifier`
class to make a copy of a classifier object:

.. code-block:: python

   from jpype import JClass

   jobject = JClass("weka.classifiers.AbstractClassifier").makeCopy(classifier.jobject)


Notes:

* `jobject` - the result of the method call, another jpype object
* `weka.classifiers.AbstractClassifier` - the classname
* `makeCopy` - the name of the static method to call
* `classifier.jobject` - the jpype object representing a classifier that is to be copied


Type conversions
----------------

The `weka.core.typeconv` module contains a number of helper functions for converting
between Java and Python objects.
