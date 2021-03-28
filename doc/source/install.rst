Installation
============

The following sections should help you install the library on your machine. Instead of installing the
library system-wide, the instructions show how to install it within in a virtual environment. This avoids
interfering with your operating system or other libraries, when you should upgrade some libraries.

Some of the instructions are based on the *CellProfiler*
`instructions <https://github.com/CellProfiler/python-javabridge/blob/master/docs/installation.rst>`__, the guys
behind the *javabridge* library.

However, if you should encounter problems or if you would like to submit improvements
on the instructions below, please use the following mailing list:

https://groups.google.com/forum/#!forum/python-weka-wrapper


Prerequisites for all platforms
-------------------------------

You need a Java Development Kit (JDK) 8 or later (e.g., `OpenJDK <https://adoptopenjdk.net/>`__) installed and
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

   $ sudo apt-get install build-essential python3-dev

Now, you can install the various packages that we require for installing
*python-weka-wrapper3*:

.. code-block:: bash

   $ sudo apt-get install python3-pip python3-numpy python3-venv

The following packages are optional, but necessary if you also want some
graphical output:

.. code-block:: bash

   $ sudo apt-get install python3-pil python3-matplotlib python3-pygraphviz

Install OpenJDK as well, in order to get all the header files that *javabridge*
compiles against (but don't use it for starting up JVMs):

.. code-block:: bash

   $ sudo apt-get install default-jdk

Create a virtual environment using the *venv* module that :

.. code-block:: bash

   $ python3 -m venv pww3


Finally, you can use ``pip`` from the virtual environment to install the Python packages that are not
available in the Ubuntu repositories:

.. code-block:: bash

   $ ./pww3/bin/pip install javabridge
   $ ./pww3/bin/pip install python-weka-wrapper3


Debian
------

First, become the superuser:

.. code-block:: bash

   $ su

You need to be able to compile C/C++ code and Python modules:

.. code-block:: bash

   $ apt-get install build-essential python3-dev

Now, you can install the various packages that we require for installing
*`python-weka-wrapper3*:

.. code-block:: bash

   $ apt-get install python3-pip python3-numpy python3-venv

The following packages are optional, but necessary if you also want some
graphical output:

.. code-block:: bash

   $ apt-get install python3-imaging python3-matplotlib python3-pygraphviz

Download a JDK and un-tar it in ``/opt`` (e.g., ``/opt/jdk-11.0.7+10/``).

Exit superuser mode and become a regular user again.

Export the Java home directory as follows, which is required for the *javabridge*
installation/compilation (you might want to add this command to your ``.profile``):

.. code-block:: bash

   $ export JAVA_HOME=/opt/jdk-11.0.7+10/

Create a virtual environment using the *venv* module that :

.. code-block:: bash

   $ python3 -m venv pww3

Finally, you can use ``pip`` from the virtual environment to install the Python packages that are not
available in the Debian repositories:

.. code-block:: bash

   $ ./pww3/bin/pip install javabridge
   $ ./pww3/bin/pip install python-weka-wrapper3

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
* install javabridge using ``./venv/bin/pip javabridge``
* install python-weka-wrapper3 using ``./venv/bin/pip python-weka-wrapper3``


Other Linux distributions
-------------------------

See `these <http://docs.python-guide.org/en/latest/starting/install/linux/>`__
general instructions for installing Python on Linux. You need to be able to
compile C/C++ code and Python modules (i.e., Python header files are required).
By installing OpenJDK, you should be able to compile *javabridge* against its
header files (for JNI access).

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

   $ python3 -m venv pww3

Once these libraries are installed, you can use ``pip`` from the virtual environment to install the Python
packages that are not available in the distro repositories:

.. code-block:: bash

   $ ./pww3/bin/pip install javabridge
   $ ./pww3/bin/pip install python-weka-wrapper3


Mac OSX
-------

Please follow `these <http://docs.python-guide.org/en/latest/starting/install/osx/>`__
general instructions for installing Python.

In order to compile C/C++ code, you need to install *Xcode* through Apple's App
Store. Once installed you can install the *XCode command-line tools* by issuing
the command ``xcode-select --install`` in a terminal.

Also, install *graphviz* using homebrew (``brew install pkg-config`` and 
``brew install graphviz``) for visualizing trees and graphs.

You need to install the following Python packages:

* numpy
* pillow
* matplotlib
* pygraphviz

Once these libraries are installed, you can use ``pip`` to install the remaining
Python packages:

.. code-block:: bash

   $ pip3 install javabridge
   $ pip3 install python-weka-wrapper3


Windows using Anaconda
----------------------

**Please note:** You need to make sure that the *bitness* of your environment
is consistent.  I.e., if you install a 32-bit version of Anaconda, you need to
install a 32-bit JDK (or all of them are 64-bit).

* download `javabridge <http://www.lfd.uci.edu/~gohlke/pythonlibs/#javabridge>`__
  for Python 3.6/3.7/3.8/3.9 (*cp36/cp37/cp38/cp39*) and your bitness (32 or 64 bit)

* the following sets up an environment with Python 3.7

  .. code-block:: bash

     > conda create --name pww3 python=3.7
     > activate pww3
     > pip install numpy
     > pip install C:\where\you\downloaded\it\javabridge-X.Y.Z.whl
     > pip install python-weka-wrapper3

If you want plotting support, then install also *graphviz* and *matplotlib*:

* download `graphviz <https://graphviz.org/download/#windows>`__
  and add the path to its installed binaries to your ``PATH`` environment variable.
* install matplotlib using ``pip install matplotlib``


Windows
-------

**Please note:** You need to make sure that the *bitness* of your environment
is consistent.  I.e., if you install a 32-bit version of Python, you need to
install a 32-bit JDK and 32-bit numpy (or all of them are 64-bit).

Perform the following steps:

* install `Python <http://www.python.org/downloads>`__, make sure you check *Add python.exe to path* during the installation
* add the Python scripts directory to your ``PATH`` environment variable, e.g., ``C:\\Python35\\Scripts``
* install ``pip`` with these steps:

 * download from `here <https://bootstrap.pypa.io/get-pip.py>`__
 * install using ``python get-pip.py``

* install numpy

 * download `numpy 1.9.x MKL <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>`__
   (or later) for Python 3.6/3.7/3.8/3.9 (*cp36/cp37/cp38/cp39*) and your *bitness* (32 or 64 bit)
 * install the *.whl* file using pip: ``pip install numpy-X.Y.Z.whl``

* install javabridge

 * download `javabridge <http://www.lfd.uci.edu/~gohlke/pythonlibs/#javabridge>`__
   (or later) for Python 3.6/3.7/3.8/3.9 (*cp36/cp37/cp38/cp39*) and your *bitness* (32 or 64 bit)
 * install the *.whl* file using pip: ``pip install javabridge-X.Y.Z.whl``

If you want to use the plotting functionality, you need to install *graphviz* and *matplotlib* as well:

* download `graphviz <https://graphviz.org/download/#windows>`__
  and add the path to its installed binaries to your ``PATH`` enrivornment variable.
* download `matplotlib <http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib>`__
  for Python 3.6/3.7/3.8/3.9 (*cp36/cp37/cp38/cp39*) and your bitness (32 or 64 bit)
* install the *.whl* file using pip: ``pip install matplotlib-X.Y.Z.whl``

.. code-block:: bash

   > pip install python-weka-wrapper3

For being able to compile libraries on Windows, you need the
`Microsoft Build Tools 2015 <https://www.microsoft.com/en-us/download/details.aspx?id=48159>`_
installed.


From source
-----------

You have two options for installing the library from source, either through a release
archive or using the *bleeding edge* source code that is available through the 
Github repository.


Release archive
+++++++++++++++

Go to the `releases <https://github.com/fracpete/python-weka-wrapper3/releases>`__ 
page on Github and download the *Source code* archive (zip or tar.gz) of the 
release that you want to install. After the download finishes, decompress the
archive. Open a terminal/command prompt and execute the following command
from within the directory with the `setup.py` file:

.. code-block:: bash

   $ ./venv/bin/python setup.py install

Check out the section on *virtualenv* as well, if you would rather install it
in a *disposable* location.


Github
++++++

Clone the Github repository as follows:

.. code-block:: bash

   git clone https://github.com/fracpete/python-weka-wrapper3.git

Change into the newly created directory and install the library using the
following command:

.. code-block:: bash

   $ ./venv/bin/python setup.py install
