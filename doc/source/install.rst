Installation
============

The following sections should help you install the library on your machine. Instead of installing the
library system-wide, the instructions show how to install it within in a virtual environment. This avoids
interfering with your operating system or other libraries, when you should upgrade some libraries.

However, if you should encounter problems or if you would like to submit improvements
on the instructions below, please use the following mailing list:

https://groups.google.com/forum/#!forum/python-weka-wrapper


Prerequisites for all platforms
-------------------------------

In the past, it was not recommended to use OpenJDK, as Weka was developed with and tested against Oracle's
version. However, Oracle's JDK 8 is no longer available for public download and OpenJDK matured enough that it is now the
recommended Java version to use. Personally, I recommend the **long-term support version 11 of OpenJDK**.

If your operating system does not offer automatic installations of JDKs, you can download OpenJDK releases for
various platforms from `here <https://adoptium.net//>`__. When manually installing an OpenJDK, you will need
to set the ``JAVA_HOME`` `environment variable <https://docs.oracle.com/cd/E21454_01/html/821-2531/inst_jdk_javahome_t.html>`__,
pointing to the installation directory.


Optional features
-----------------

Support for plots and graphs are optional features. If you do not want or need these, you can
omit the suffix ``[plots,graphs]`` when installing python-weka-wrapper3.


Ubuntu
------

A video demonstrating the installation on Ubuntu 22.04 is available:
`https://youtu.be/UIm0rKilABc?si=DUECgNdc16K64CCu <https://youtu.be/UIm0rKilABc?si=DUECgNdc16K64CCu>`__

First, you need to be able to compile C/C++ code and Python modules:

.. code-block:: bash

   sudo apt install build-essential python3-dev

Now, you can install the various packages that we require for installing
*python-weka-wrapper3*:

.. code-block:: bash

   sudo apt install python3-pip python3-numpy python3-venv

The following packages are optional, but necessary if you also want some
graphical output:

.. code-block:: bash

   sudo apt install python3-pil python3-matplotlib python3-pygraphviz libgraphviz-dev

Install OpenJDK as well, in order to get all the header files for compilation:

.. code-block:: bash

   sudo apt install openjdk-11-jdk

Create a virtual environment using the *venv* module that :

.. code-block:: bash

   python3 -m venv pww3

Finally, you can use ``pip`` from the virtual environment to install the Python packages that are not
available in the Ubuntu repositories:

.. code-block:: bash

   . ./pww3/bin/activate
   pip install setuptools wheel
   pip install python-weka-wrapper3[plots,graphs]


Debian
------

First, become the superuser:

.. code-block:: bash

   su

You need to be able to compile C/C++ code and Python modules:

.. code-block:: bash

   apt install build-essential python3-dev

Now, you can install the various packages that we require for installing
*`python-weka-wrapper3*:

.. code-block:: bash

   apt install python3-pip python3-numpy python3-venv

The following packages are optional, but necessary if you also want some
graphical output:

.. code-block:: bash

   apt install python3-pil python3-matplotlib python3-pygraphviz libgraphviz-dev

Older Debian versions used `python3-imaging` instead of `python3-pil`.

Download a JDK and un-tar it in ``/opt`` (e.g., ``/opt/jdk-11.0.23+9/``).

Exit superuser mode and become a regular user again.

Export the Java home directory as follows (you might want to add this command to your ``.profile``):

.. code-block:: bash

   export JAVA_HOME=/opt/jdk-11.0.23+9/

Create a virtual environment using the *venv* module that :

.. code-block:: bash

   python3 -m venv pww3

Once the environment is set up, activate it and install *python-weka-wrapper3*:

.. code-block:: bash

   . ./pww3/bin/activate
   pip install setuptools wheel
   pip install python-weka-wrapper3[plots,graphs]

Please note, when using *python-weka-wrapper3* as a *normal* user, don't forget
to export the ``JAVA_HOME`` environment variable as described above (e.g., add it
to your ``.profile``).


Fedora/CentOS/Redhat
--------------------

Here are some rough instructions (as superuser):

* install openjdk (+ -devel) package
* install python (+ -devel) package
* download pip from https://bootstrap.pypa.io/get-pip.py
* install pip using ``python get-pip.py``
* install dev tools using ``yum groupinstall "Development tools"``
* install numpy package
* install python-imaging package (shouldn't be necessary)

Switch back to being a regular user.

Create a virtual environment using the *venv* module that :

.. code-block:: bash

   python3 -m venv pww3

Finally, you can use ``pip`` from the virtual environment to install the Python packages that are not
available in the Ubuntu repositories:

.. code-block:: bash

   . ./pww3/bin/activate
   pip install setuptools wheel
   pip install python-weka-wrapper3[plots,graphs]


Other Linux distributions
-------------------------

See `these <http://docs.python-guide.org/en/latest/starting/install/linux/>`__
general instructions for installing Python on Linux. You need to be able to
compile C/C++ code and Python modules (i.e., Python header files are required).
By installing OpenJDK, you should be able to compile against its header files.

Then you need to install the following Python packages, preferably through your
package manager (e.g., ``yum``).  Please note that on a *headless* machine, you
can omit the packages marked as *optional*, as they are only required for
graphical output and plots:

* pip3
* numpy
* PIL (optional)
* matplotlib (optional)
* pygraphviz (optional; requires graphviz headers)

Create a virtual environment using the *venv* module that :

.. code-block:: bash

   python3 -m venv pww3

Once the environment is set up, activate it and install *python-weka-wrapper3*:

.. code-block:: bash

   . ./pww3/bin/activate
   pip install setuptools wheel
   pip install python-weka-wrapper3[plots,graphs]


COLAB
-----

In a Python 3 COLAB environment, you need to run the following steps for full functionality:

.. code-block:: bash

   # install dependencies
   !apt install build-essential python3-dev
   !apt install python3-pil python3-pygraphviz libgraphviz-dev
   !apt install openjdk-11-jdk
   # install pww3
   !pip install wheel
   !pip install python-weka-wrapper3[plots,graphs]


**Notes:**

* Once the JVM has been stopped, you will have to restart the COLAB runtime
* After installing packages, you need to restart the COLAB runtime, otherwise the packages won't be available to the JVM


Mac OSX
-------

Please follow `these <http://docs.python-guide.org/en/latest/starting/install/osx/>`__
general instructions for installing Python.

Create a virtual environment using the *venv* module:

.. code-block:: bash

   python3 -m venv pww3

Once the environment is set up, activate it and install *python-weka-wrapper3*:

.. code-block:: bash

   . ./pww3/bin/activate
   pip install wheel
   brew install graphviz
   python3 -m pip install graphviz
   python3 -m pip install -U --no-cache-dir --config-settings="--global-option=build_ext" --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" pygraphviz
   pip install python-weka-wrapper3[plots,graphs]


Windows using Anaconda
----------------------

A video demonstrating the installation on Windows 10 is available:
`https://youtu.be/azr-JqF7jLE?si=JAz9M9NhJ5kVvWY0 <https://youtu.be/azr-JqF7jLE?si=JAz9M9NhJ5kVvWY0>`__

* download and install `Anaconda <https://www.anaconda.com/download/>`__ if you haven't done so already
* the following configures an environment with Python 3.12

  .. code-block:: doscon

     conda create --name pww3 python=3.12
     conda activate pww3
     conda install -c conda-forge setuptools wheel pillow matplotlib lxml pygraphviz
     pip install python-weka-wrapper3[plots,graphs]



Windows
-------

**Please note:** You need to make sure that the *bitness* of your environment
is consistent.  I.e., if you install a 32-bit version of Python, you need to
install a 32-bit JDK (or all of them are 64-bit).

A video demonstrating the installation on Windows 10 (without graph support) is available:
`https://youtu.be/t5g9cigltvs?si=-RkcZT1ygSJTjT2E <https://youtu.be/t5g9cigltvs?si=-RkcZT1ygSJTjT2E>`__

Perform the following steps:

* if you want to be able to *display graphs in dot format* (very large installation):

  * download and install the `.Net framework 4.6 or later <https://dotnet.microsoft.com/en-us/download/dotnet-framework/>`__ (required for Visual C++ Build Tools)
  * download and install the `Visual C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`__,
    select the **Desktop development with C++** option in the installer
  * install `GraphViz <https://graphviz.org/download/>`__ into ``C:\Program Files\Graphviz`` and add its binaries to
    the ``PATH`` environment variable

* if you do not need *dot format support*:

  * install `MS VC++ redistributable <https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#latest-microsoft-visual-c-redistributable-version>`__

* install `Python <http://www.python.org/downloads>`__, make sure you check *Add python.exe to path* during the installation
* open a command-prompt and create a virtual environment
* create a virtual environment using the *venv* module:

.. code-block:: doscon

   python -m venv pww3

Once the environment is set up, activate it and install *python-weka-wrapper3*:

.. code-block:: doscon

   pww3\Scripts\activate
   pip install setuptools wheel

If you installed *Visual C++ Build Tools* and *Graphviz*:

.. code-block:: doscon

   pip install -U --no-cache-dir --config-settings="--global-option=build_ext" --config-settings="--global-option=-IC:\\Program Files\\Graphviz\\include" --config-settings="--global-option=-LC:\\Program Files\\Graphviz\\lib" pygraphviz
   pip install python-weka-wrapper3[plots,graphs]

If you only installed *MS VC++ redistributable*:

.. code-block:: doscon

   pip install python-weka-wrapper3[plots]


From source
-----------

You can install python-weka-wrapper3 directly from its Github repository with `pip`
as follows (e.g., to get the latest fixes/features):


First, create a virtual environment:

.. code-block:: bash

   python3 -m venv pww3

Once the environment is set up, activate it and install *python-weka-wrapper3*:

.. code-block:: bash

   . ./pww3/bin/activate
   pip install "python-weka-wrapper3[plots,graphs] @ git+https://github.com/fracpete/python-weka-wrapper3.git"
