Development
===========

The Python code of the *python-weka-wrapper3* library shields the user from the
complicated Java Native Interface (JNI) calls that are required to communicate
with objects in the Java Virtual Machine (JVM). However, there may be times
that additional or missing access methods need to be


JNI Signatures
--------------

Documentation on JNI signatures can be found here:

`https://docs.oracle.com/en/java/javase/17/docs/specs/jni/types.html#type-signatures <https://docs.oracle.com/en/java/javase/17/docs/specs/jni/types.html#type-signatures>`__


javap
-----

`javap` is a little tool that is bundled with a JDK and can be used for outputting the
internal (aka JNI) signatures of methods. The following outputs the signatures
of the `weka.classifiers.Classifier` interface:

.. code-block:: bash

   javap -cp weka.jar -s weka.classifiers.Classifier

The output will look like this:

::

    Compiled from "Classifier.java"
    public interface weka.classifiers.Classifier {
      public abstract void buildClassifier(weka.core.Instances) throws java.lang.Exception;
        descriptor: (Lweka/core/Instances;)V

      public abstract double classifyInstance(weka.core.Instance) throws java.lang.Exception;
        descriptor: (Lweka/core/Instance;)D

      public abstract double[] distributionForInstance(weka.core.Instance) throws java.lang.Exception;
        descriptor: (Lweka/core/Instance;)[D

      public abstract weka.core.Capabilities getCapabilities();
        descriptor: ()Lweka/core/Capabilities;
    }


Calling methods
---------------

Non-static methods
++++++++++++++++++

For calling a **non-static method**, you can use the `call` method of the `javabridge` module.
You have to provide the Javabridge object, the method name, its JNI signature and any
parameters that the method requires.

Here is a code snippet that calls the `buildClassifier` method of a `weka.classifiers.Classifier`
object:

.. code-block:: python

   javabridge.call(self.jobject, "buildClassifier", "(Lweka/core/Instances;)V", data.jobject)


Notes:

* `self.jobject` - the Javabridge object representing the classifier Java object
* `buildClassifier` - the method that we want to call
* `(Lweka/core/Instances;)V` - the signature obtained via `javap`
* `data.object` - the Javabridge object representing a `weka.core.Instances` object


Static methods
++++++++++++++

For calling a **static method**, Javabridge offers the `static_call` method.
Below is an example for calling the `makeCopy` method of the `weka.classifiers.AbstractClassifier`
class to make a copy of a classifier object:

.. code-block:: python

   jobject = javabridge.static_call(
       "weka/classifiers/AbstractClassifier", "makeCopy",
       "(Lweka/classifiers/Classifier;)Lweka/classifiers/Classifier;", classifier.jobject)


Notes:

* `jobject` - the result of the method call, another Javabridge object
* `weka/classifiers/AbstractClassifier` - the classname, using forward slashes instead of dots
* `makeCopy` - the name of the static method to call
* `(Lweka/classifiers/Classifier;)Lweka/classifiers/Classifier;` - the signature of the method
* `classifier.jobject` - the Javabridge object representing a classifier that is to be copied


JWrapper and JClassWrapper
++++++++++++++++++++++++++

Later versions of Javabridge also introduced a simpler way of calling methods:

* `javabridge.JWrapper`
* `javabridge.JClassWrapper`

The first one is used to wrap around a *Java object*, giving access to its methods using dot notation.
The second is to be wrapped around a *Java class*, in order to gain access to its methods via dot notation.

*python-weka-wrapper3* offers convenience properties for these two wrappers, as implemented by
the `weka.core.classes.JavaObject` class:

* `jwrapper`
* `jclasswrapper`

For example, for accessing the `getMeasure(String)` method of the J48 classifier
(as it implements the `weka.core.AdditionalMeasureProducer` interface) to retrieve
the number of leaves in the tree, you can do the following:

.. code-block:: python

   data = ...  # the training data
   cls = Classifier(classname="weka.classifiers.trees.J48")
   cls.build_classifier(data)
   # call getMeasure(String)
   print(cls.jwrapper.getMeasure("measureNumLeaves"))


The same call using JNI calls would look like this:

.. code-block:: python

   data = ...  # the training data
   cls = Classifier(classname="weka.classifiers.trees.J48")
   cls.build_classifier(data)
   # call getMeasure(String)
   print(javabridge.call(cls.jobject, "getMeasure", "(Ljava/lang/String;)D", "measureNumLeaves"))


Type conversions
----------------

The `weka.core.typeconv` module contains a number of helper functions for converting
between Java and Python objects.
