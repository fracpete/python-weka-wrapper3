Installation
============

The following sections should help you install the library on your machine.

Some of the instructions are based on the *CellProfiler*
`instructions <https://github.com/CellProfiler/python-javabridge/blob/master/docs/installation.rst>`__, the guys
behind the *javabridge* library.

However, if you should encounter problems or if you would like to submit improvements
on the instructions below, please use the following mailing list:

https://groups.google.com/forum/#!forum/python-weka-wrapper


Videos
------

You can find videos on `YouTube <https://www.youtube.com/channel/UCYkzno8dbnAasWakSXVsuPA>`__ that show the installation process:

* `Ubuntu 14.04 (64-bit) <https://www.youtube.com/watch?v=8d0PVBlttM4>`__
* `Windows 7 (32-bit) <https://www.youtube.com/watch?v=KdDt9rT5wTo>`__
* `Windows 8.1 (64-bit) <https://www.youtube.com/watch?v=PeUfDVOA_1Y>`__
* `Mac OSX 10.9.5 (Mavericks) <https://www.youtube.com/watch?v=CORXWYam36E>`__


Prerequisites for all plaforms
------------------------------

You need an `Oracle JDK (1.7+)
<http://www.oracle.com/technetwork/java/javase/downloads/>`__ installed and
the ``JAVA_HOME`` `environment variable
<http://docs.oracle.com/cd/E19182-01/820-7851/inst_cli_jdk_javahome_t/index.html>`__
pointing to the installation directory in order to use *python-weka-wrapper*
library.

*Why not OpenJDK?* Weka is developed and tested with Oracle's JDK/JRE. There is
no guarantee that it will work with OpenJDK.


Ubuntu
------

First, you need to be able to compile C/C++ code and Python modules:

.. code-block:: bash

   $ sudo apt-get install build-essential python-dev

Now, you can install the various packages that we require for installing
*python-weka-wrapper*:

.. code-block:: bash

   $ sudo apt-get install python-pip python-numpy

The following packages are optional, but necessary if you also want some
graphical output:

.. code-block:: bash

   $ sudo apt-get install python-imaging python-matplotlib python-pygraphviz

Install OpenJDK as well, in order to get all the header files that *javabridge*
compiles against (but don't use it for starting up JVMs):

.. code-block:: bash

   $ sudo apt-get install default-jdk

Finally, you can use ``pip`` to install the Python packages that are not
available in the repositories:

.. code-block:: bash

   $ sudo pip install javabridge
   $ sudo pip install python-weka-wrapper


Debian
------

First, become the superuser:

.. code-block:: bash

   $ su

You need to be able to compile C/C++ code and Python modules:

.. code-block:: bash

   $ apt-get install build-essential python-dev

Now, you can install the various packages that we require for installing
*`python-weka-wrapper*:

.. code-block:: bash

   $ apt-get install python-pip python-numpy

The following packages are optional, but necessary if you also want some
graphical output:

.. code-block:: bash

   $ apt-get install python-imaging python-matplotlib python-pygraphviz

Download an Oracle JDK and un-tar it in ``/opt`` (e.g., ``/opt/jdk1.7.0_75/``).
Export the Java home directory as follows (required for the *javabridge*
installation):

.. code-block:: bash

   $ export JAVA_HOME=/opt/jdk1.7.0_75/

Finally, you can use ``pip`` to install the Python packages that are not
available in the repositories:

.. code-block:: bash

   $ pip install javabridge
   $ pip install python-weka-wrapper

Please note, when using *python-weka-wrapper* as a *normal* user, don't forget
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
* install javabridge using ``pip javabridge``
* install python-weka-wrapper using ``pip python-weka-wrapper``


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

* pip
* numpy
* PIL (optional)
* matplotlib (optional)
* pygraphviz (optional)

Once these libraries are installed, you can use ``pip`` to install the remaining
Python packages:

.. code-block:: bash

   $ sudo pip install javabridge
   $ sudo pip install python-weka-wrapper


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

   $ pip install javabridge
   $ pip install python-weka-wrapper


Windows
-------

**Please note:** You need to make sure that the *bitness* of your environment
is consistent.  I.e., if you install a 32-bit version of Python, you need to
install a 32-bit JDK and 32-bit numpy (or all of them are 64-bit).

Perform the following steps:

* install `Python <http://www.python.org/downloads>`__, make sure you check *Add python.exe to path* during the installation
* add the Python scripts directory to your ``PATH`` environment variable, e.g., ``C:\\Python27\\Scripts``
* install ``pip`` with these steps:

 * download from `here <https://bootstrap.pypa.io/get-pip.py>`__
 * install using ``python get-pip.py``

* install numpy

 * download `numpy 1.9.x MKL <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>`__
   (or later) for Python 2.7 (*cp27*) and your *bitness* (32 or 64 bit)
 * install the *.whl* file using pip: ``pip install numpy-X.Y.Z.whl``

* install `.Net 4.0 <http://go.microsoft.com/fwlink/?LinkID=187668>`__ (if not
  already installed)
* install `Windows SDK 7.1 <http://www.microsoft.com/download/details.aspx?id=8279>`__

* open Windows SDK command prompt (**not** the regular command prompt!) and install *javabridge* and *python-weka-wrapper*

  .. code-block:: bat

     set MSSdk=1
     set DISTUTILS_USE_SDK=1
     pip install javabridge
     pip install python-weka-wrapper

Now you can run *python-weka-wrapper* using the regular command-prompt as well.

If you want to use the plotting functionality, you need to install *matplotlib* as well:

* download `matplotlib <http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib>`__
  for Python 2.7 (*cp27*) and your bitness (32 or 64 bit)
* install the *.whl* file using pip: ``pip install matplotlib-X.Y.Z.whl``


From source
-----------

You have two options for installing the library from source, either through a release
archive or using the *bleeding edge* source code that is available through the 
Github repository.


Archive
+++++++

Go to the `releases <https://github.com/fracpete/python-weka-wrapper3/releases>`__ 
page on Github and download the *Source code* archive (zip or tar.gz) of the 
release that you want to install. After the download finishes, decompress the
archive. Open a terminal/command prompt and execute the following command
from within the directory with the `setup.py` file:

.. code-block:: bash

   $ python setup.py install

Check out the section on *virtualenv* as well, if you would rather install it
in a *disposable* location.


Gtihub
++++++

Clone the Github repository as follows:

.. code-block:: bash

   git clone https://github.com/fracpete/python-weka-wrapper3.git

Change into the newly created directory and install the library using the
following command:

.. code-block:: bash

   $ python setup.py install

Check out the section on *virtualenv* as well, if you would rather install it
in a *disposable* location.

