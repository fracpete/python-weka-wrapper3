Troubleshooting
===============

General
-------

* **Q:** How do I install `.whl` files?

  **A:** `.whl` are *Python Wheels* archives, which you can install using pip (>= 1.4). See also `this website <http://pythonwheels.com/>`_.

* **Q:** Packages don't get loaded and/or you see exceptions of the type 
  ``java.lang.ClassNotFoundException: org.pentaho.packageManagement.DefaultPackage``
  output in the terminal. What is the cause?

  **A:** Weka 3.7.13 contained some severe bugs (filtering data, extremely slow option
  handling), which prompted me to include a Weka jar built from sources after the
  3.7.13 release. Unfortunately, the Weka package manager changed during this period
  as well and the serialized cache file is not compatible between these versions. 
  Running Weka 3.7.13 and python-weka-wrapper 0.3.5 in parallel can therefore render
  package handling inoperable. However, you can simply delete the cache file
  (``installedPackageCache.ser``) and restart either application. This file is
  located here:

  * Linux/Mac: ``$HOME/wekafiles/packages/installedPackageCache.ser``
  * Windows: ``%USERPROFILE%\wekafiles\packages\installedPackageCache.ser``


Debian
------

* **Q:** On a headless Debian server, building a classifier can result in Python exiting, printing the error message
  `GConf Error: Failed to contact configuration server; some possible causes are that you need to enable TCP/IP
  networking for ORBit, or you have stale NFS locks due to a system crash. See http://projects.gnome.org/gconf/
  for information. (Details -  1: Not running within active session)`. How to fix?

  **A:** According to `this <http://stackoverflow.com/questions/1421498/linux-gedit-i-always-get-gconf-error-failed-to-contact-configuration-server>`_
  post, set the following environment variable:

  .. code-block:: bash

     export DBUS_SESSION_BUS_ADDRESS=""

  And make sure that the `~/.dbus` directory has 0700 as permission mask.


Ubuntu
------

* **Q:** On a headless Ubuntu server, building a classifier can result in Python exiting, printing the error message
  `GLib-GIO-ERROR **: Settings schema 'org.gnome.system.proxy' is not installed`. How to fix?

  **A:** Simply run the following command to fix this:
  `sudo apt-get install gsettings-desktop-schemas`


Mac OSX
-------

* **Q:** Why does javabridge fail with compiler error `clang: error: unknown argument: '-mno-fused-madd'`?

  **A:** XCode 5.1 changed how unknown arguments are handled and now treats them  as error (`source <http://bruteforce.gr/bypassing-clang-error-unknown-argument.html>`_). You can precede the `pip install javabridge` command with the following environment variable:

  .. code-block:: bash

     ARCHFLAGS="-Wno-error=unused-command-line-argument-hard-error-in-future" pip install javabridge

* **Q:** Compiling javabridge fails with missing `jni.h` header file - what now?

  **A:** You will need an Oracle JDK installed for this. `Download <http://www.oracle.com/technetwork/java/javase/downloads/>`_ and install one. Below is a command-line that uses the `jni.h` header file that comes with `1.7.0_45`:

  .. code-block:: bash

     ARCHFLAGS="-I/Library/Java/JavaVirtualMachines/jdk1.7.0_45.jdk/Contents/Home/include/ -I/Library/Java/JavaVirtualMachines/jdk1.7.0_45.jdk/Contents/Home/include/darwin" pip install --user javabridge

  *PS:* You may need to combine the `ARCHFLAGS` setting with the one from the previous Q&A.

* **Q:** When I use `import javabridge` in my Python shell, a
  dialog pops up, telling me that I don't have Java installed. However, I have
  an Oracle JDK installed. What's wrong?

  **A:** Java environments that are not from Apple don't seem to get picked up
  by Python correctly. Simply install the Java 1.6 that Apple supplies on your
  system as well.

* **Q:** Installing `pygraphviz` fails, because it cannot find the library or
  its includes. What now?

  **A:** Here is what to do:
    * Make sure that you have the `GraphViz <http://graphviz.org/Download_macos.php>`_ 
      package installed.

    * If the installer is still not finding the libraries, download the 
      `pygraphviz <https://pypi.python.org/pypi/pygraphviz>`_ sources from PyPi and 
      extract them.

    * Open the `setup.py` file in a text editor and set the `library_path` and
      `include_path` variables to the correct paths on your machine, e.g.,
      `library_path=/usr/local/lib/graphviz` and
      `include_path=/usr/local/include/graphviz` and save the file.

    * Open a terminal and navigate to the directory where the `setup.py` file
      is located that you just edited.

    * Install the package using `python setup.py install --user`


* **Q:** Installing `pygraphviz` fails with error message 
  `ld: library not found for -lcgraph`. What is wrong?

  **A:** Apparently, the XCode command-line are not installed. You can install
  them by opening a terminal and running the following command: 
  `xcode-select --install`


Windows
-------

* **Q:** The Windows SDK 7.1 installer fails (eg when behind a proxy). What now?

  **A:** You can download an ISO image of the SDK from
  `here <http://www.microsoft.com/en-us/download/details.aspx?id=8442>`_
  (`GRMSDK_EN_DVD.iso` is the 32-bit version and `GRMSDKX_EN_DVD.iso` is the 64-bit version).
  See `this HOWTO <http://www.howtogeek.com/howto/windows-vista/mount-an-iso-image-in-windows-vista/>`_
  for mounting the ISO image once downloaded.

* **Q:** I cannot display graphs, e.g., generated by J48, as I keep getting the error message `ValueError: Program dot not found in path.` - what can I do?

  **A:** PyGraphviz is just a wrapper for `GraphViz <http://www.graphviz.org/>`_ which you
  you need to install separately. Also, you need to add the directory containing the GraphViz binaries, like `dot.exe`, to the `PATH` environment variable, e.g., `C:\\Program Files (x86)\\Graphviz2.38\\bin` (you may have to log out and back in again for these changes to take effect).


