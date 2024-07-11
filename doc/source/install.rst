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

You need a Java Development Kit (JDK) 8 or later (e.g., `OpenJDK <https://adoptium.net//>`__) installed and
the ``JAVA_HOME`` `environment variable
<http://docs.oracle.com/cd/E19182-01/820-7851/inst_cli_jdk_javahome_t/index.html>`__
pointing to the installation directory in order to use *python-weka-wrapper3*
library.

**Note:** In the past, it was not recommended to use OpenJDK, as Weka was developed with and tested against Oracle's
version. However, Oracle's JDK 8 is no longer available for public download and OpenJDK matured enough that it is now the
recommended Java version to use. Personally, I recommend the **long-term support version 11 of OpenJDK**.


Ubuntu
------

First, you need to be able to compile C/C++ code and Python modules:

.. code-block:: bash

   sudo apt-get install build-essential python3-dev

Now, you can install the various packages that we require for installing
*python-weka-wrapper3*:

.. code-block:: bash

   sudo apt-get install python3-pip python3-numpy python3-venv

The following packages are optional, but necessary if you also want some
graphical output:

.. code-block:: bash

   sudo apt-get install python3-pil python3-matplotlib python3-pygraphviz

Install OpenJDK as well, in order to get all the header files for compilation:

.. code-block:: bash

   sudo apt-get install default-jdk

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

   apt-get install build-essential python3-dev

Now, you can install the various packages that we require for installing
*`python-weka-wrapper3*:

.. code-block:: bash

   apt-get install python3-pip python3-numpy python3-venv

The following packages are optional, but necessary if you also want some
graphical output:

.. code-block:: bash

   apt-get install python3-pil python3-matplotlib python3-pygraphviz

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

As regular user:

* create a virtual environment (see Ubuntu/Debian sections above)
* activate the virtual environment using ``. ./venv/bin/activate``
* install wheel using ``pip wheel``
* install python-weka-wrapper3 using ``pip python-weka-wrapper3[plots,graphs]``


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
* pygraphviz (optional)

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
   !apt-get install build-essential python3-dev
   !apt-get install python3-pil python3-pygraphviz
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

**Please note:** You need to make sure that the *bitness* of your environment
is consistent.  I.e., if you install a 32-bit version of Anaconda, you need to
install a 32-bit JDK (or all of them are 64-bit).

* set the `JDK_HOME` environment variable to point at the same directory as `JAVA_HOME`
* download and install the `Visual C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`__,
  select the **Desktop development with C++** option in the installer
* the following configures an environment with Python 3.12

  .. code-block:: doscon

     conda create --name pww3 python=3.12
     conda activate pww3
     conda install -c conda-forge setuptools wheel pillow matplotlib lxml pygraphviz
     pip install python-weka-wrapper3[plots,graphs]

For *graphviz* support you also need the Windows binary installed:

* download `graphviz <https://graphviz.org/download/#windows>`__
* add the path to its installed binaries to your ``PATH`` environment variable.


Windows
-------

**Please note:** You need to make sure that the *bitness* of your environment
is consistent.  I.e., if you install a 32-bit version of Python, you need to
install a 32-bit JDK (or all of them are 64-bit).

Perform the following steps:

* set the `JDK_HOME` environment variable to point at the same directory as `JAVA_HOME`
* download and install the `Visual C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`__,
  select the **Desktop development with C++** option in the installer
* install `Python <http://www.python.org/downloads>`__, make sure you check *Add python.exe to path* during the installation
* add the Python scripts directory to your ``PATH`` environment variable, e.g., ``C:\\Python312\\Scripts``
* open a command-prompt and create a virtual environment
* create a virtual environment using the *venv* module:

.. code-block:: doscon

   python -m venv pww3

Once the environment is set up, activate it and install *python-weka-wrapper3*:

.. code-block:: doscon

   pww3\Scripts\activate
   pip install setuptools wheel
   pip install python-weka-wrapper3[plots,graphs]

For *graphviz* support you also need the Windows binary installed:

* download `graphviz <https://graphviz.org/download/#windows>`__
* add the path to its installed binaries to your ``PATH`` environment variable.


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
