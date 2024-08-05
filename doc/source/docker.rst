Docker
======

In order to make installation reproducible, `Docker <https://www.docker.com/>`__
images for various python-weka-wrapper3 versions are available from Docker Hub:

`fracpete/pww3/tags <https://hub.docker.com/r/fracpete/pww3/tags>`__

If you are unfamiliar with Docker, then have a look at the following
introduction for Data Scientists:

`data-mining.co.nz/docker-for-data-scientists/ <https://www.data-mining.co.nz/docker-for-data-scientists/>`__


Images
------

CPU
+++

For using the CPU image interactively, you can run the following command:

.. code-block:: bash

   docker run -u $(id -u):$(id -g) \
       -it fracpete/pww3:0.3.2_cpu

Instead of having to reinstall your packages each time you start up the container,
you can map your local Weka packages into the container as follows:

.. code-block:: bash

   docker run -u $(id -u):$(id -g) \
       -v $HOME/wekafiles/:/workspace/wekafiles \
       -it fracpete/pww3:0.3.2_cpu


GPU
+++

**DEPRECATED: Starting with version 0.2.15, no more GPU images will be provided as NVIDIA deleted the underlying CUDA 10.2 image.**

For using the GPU image interactively, you can run the following command:

.. code-block:: bash

   docker run --gpus=all -u $(id -u):$(id -g) \
       -it fracpete/pww3:0.2.14_cuda10.2

Instead of having to reinstall your packages each time you start up the container,
you can map your local Weka packages into the container as follows:

.. code-block:: bash

   docker run --gpus=all -u $(id -u):$(id -g) \
       -v $HOME/wekafiles/:/workspace/wekafiles \
       -it fracpete/pww3:0.2.14_cuda10.2


Usage
-----

Executables
+++++++++++

Since python-weka-wrapper3 installs executables for the main class hierarchies
of Weka, you can run these directly with a single command.

E.g., if we want to train a J48 classifier on the dataset `anneal.arff` which
is in our current directory (`pwd`), then we can do something like this:

.. code-block:: bash

   docker run --rm -u $(id -u):$(id -g) \
       -v $HOME/wekafiles:/workspace/wekafiles \
       -v `pwd`:/workspace/data \
       -t fracpete/pww3:0.3.2_cpu \
       pww-classifier \
       -t /workspace/data/anneal.arff \
       weka.classifiers.trees.J48


Scripts
+++++++

For more flexibility and/or more complex operations, you would normally want to
fall back on using Python scripts. The above example can be translated into
the following Python script (saved in current directory as `j48.py`):

.. code-block:: python

   import weka.core.jvm as jvm
   from weka.core.classes import Random
   from weka.core.converters import load_any_file
   from weka.classifiers import Classifier, Evaluation

   jvm.start()

   data = load_any_file("/workspace/data/anneal.arff", class_index="last")
   cls = Classifier(classname="weka.classifiers.trees.J48")
   evl = Evaluation(data)
   evl.crossvalidate_model(cls, data, 10, Random(1))
   print(evl.summary())

   jvm.stop()


This script is then executed as follows:

.. code-block:: bash

   docker run --rm -u $(id -u):$(id -g) \
       -v $HOME/wekafiles:/workspace/wekafiles \
       -v `pwd`:/workspace/data \
       -t fracpete/pww3:0.3.2_cpu \
       python3 /workspace/data/j48.py


Installing Weka packages
------------------------

When building Docker images for your environments, your code will most likely rely
on additional Weka packages. You can install the packages by creating a little
Python script that uses python-weka-wrapper3 to install them (just like you would
normally do in a script). Here is the content of the ``install_packages.py``
script:

.. code-block:: python

   import weka.core.jvm as jvm
   import weka.core.packages as packages

   jvm.start(packages=True)

   # for reproducibility, we also specify the version
   packages.install_package("SelfOrganizingMap", version="1.0.3")

   jvm.stop()


A minimal ``Dockerfile`` (in the same directory as ``install_packages.py``) then looks
like this (using pww3 0.2.14 for CPU):

::

   FROM fracpete/pww3:0.3.2_cpu
   COPY install_packages.py /workspace/install_packages.py
   RUN python3 /workspace/install_packages.py


You can then build this image just like any other Docker image:

.. code-block:: bash

   docker build -t pww3-pkg .


For testing, you can create a local script called ``test_packages.py`` with
the content similar to this:

.. code-block:: python

   import weka.core.jvm as jvm
   import weka.core.packages as packages
   from weka.clusterers import Clusterer

   jvm.start(packages=True)

   # list packages
   items = packages.installed_packages()
   for item in items:
       print(item.name + "/" + item.version + "\n  " + item.url)

   # instantiate from package
   cls = Clusterer(classname="weka.clusterers.SelfOrganizingMap")
   print(cls.to_commandline())

   jvm.stop()


The following command simply runs our ``test_packages.py`` script. To achieve this,
the command maps the current directory (``pwd``) into the container's ``/workspace/scripts``
directory:

.. code-block:: bash

   docker run \
       -v `pwd`:/workspace/scripts \
       -t pww3-pkg:latest \
       python3 /workspace/scripts/test_packages.py


The output will be something like this:

::

   DEBUG:weka.core.jvm:Adding bundled jars
   DEBUG:weka.core.jvm:Classpath=...
   DEBUG:weka.core.jvm:MaxHeapSize=default
   DEBUG:weka.core.jvm:Package support enabled
   SelfOrganizingMap/1.0.3
     http://prdownloads.sourceforge.net/wekann/SelfOrganizingMap1.0.3.zip?download
   weka.clusterers.SelfOrganizingMap -L 1.0 -O 2000 -C 1000 -H 2 -W 2

