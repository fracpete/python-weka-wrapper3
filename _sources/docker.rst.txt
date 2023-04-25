Docker
======

In order to make installation reproducible, `Docker <https://www.docker.com/>`__
images for various python-weka-wrapper3 versions are available from Docker Hub:

`fracpete/pww3/tags <https://hub.docker.com/r/fracpete/pww3/tags>`__

If you are unfamiliar with Docker, then have a look at the following
introduction for Data Scientists:

`data-mining.co.nz/docker-for-data-scientists/ <https://www.data-mining.co.nz/docker-for-data-scientists/>`__


CPU
---

For using the image interactively, you can run the following command:

.. code-block:: bash

   docker run -u $(id -u):$(id -g) \
       -it fracpete/pww3:0.2.13_cpu

Instead of having to reinstall your packages each time you start up the container,
you can map your local Weka packages into the container as follows:

.. code-block:: bash

   docker run -u $(id -u):$(id -g) \
       -v $HOME/wekafiles/:/workspace/wekafiles \
       -it fracpete/pww3:0.2.13_cpu


GPU
---

For using the image interactively, you can run the following command:

.. code-block:: bash

   docker run --gpus=all -u $(id -u):$(id -g) \
       -it fracpete/pww3:0.2.13_cuda10.2

Instead of having to reinstall your packages each time you start up the container,
you can map your local Weka packages into the container as follows:

.. code-block:: bash

   docker run --gpus=all -u $(id -u):$(id -g) \
       -v $HOME/wekafiles/:/workspace/wekafiles \
       -it fracpete/pww3:0.2.13_cuda10.2


Additional Weka packages
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
like this (using pww3 0.2.13 for CPU):

::

   FROM fracpete/pww3:0.2.13_cpu
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
   DEBUG:weka.core.jvm:Classpath=['/usr/local/lib/python3.8/dist-packages/javabridge/jars/rhino-1.7R4.jar', '/usr/local/lib/python3.8/dist-packages/javabridge/jars/runnablequeue.jar', '/usr/local/lib/python3.8/dist-packages/javabridge/jars/cpython.jar', '/usr/local/lib/python3.8/dist-packages/weka/lib/weka.jar', '/usr/local/lib/python3.8/dist-packages/weka/lib/python-weka-wrapper.jar']
   DEBUG:weka.core.jvm:MaxHeapSize=default
   DEBUG:weka.core.jvm:Package support enabled
   SelfOrganizingMap/1.0.3
     http://prdownloads.sourceforge.net/wekann/SelfOrganizingMap1.0.3.zip?download
   weka.clusterers.SelfOrganizingMap -L 1.0 -O 2000 -C 1000 -H 2 -W 2

