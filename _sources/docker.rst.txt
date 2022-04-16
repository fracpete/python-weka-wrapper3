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
       -it fracpete/pww3:0.2.9_cpu

Instead of having to reinstall your packages each time you start up the container,
you can map your local Weka packages into the container as follows:

.. code-block:: bash

   docker run -u $(id -u):$(id -g) \
       -v $HOME/wekafiles/:/workspace/wekafiles \
       -it fracpete/pww3:0.2.9_cpu


GPU
---

For using the image interactively, you can run the following command:

.. code-block:: bash

   docker run --gpus=all -u $(id -u):$(id -g) \
       -it fracpete/pww3:0.2.9_cuda10.2

Instead of having to reinstall your packages each time you start up the container,
you can map your local Weka packages into the container as follows:

.. code-block:: bash

   docker run --gpus=all -u $(id -u):$(id -g) \
       -v $HOME/wekafiles/:/workspace/wekafiles \
       -it fracpete/pww3:0.2.9_cuda10.2
