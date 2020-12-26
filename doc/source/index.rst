.. python-weka-wrapper3 documentation master file, created by
   sphinx-quickstart on Sat Apr 12 11:51:06 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============

*python-weka-wrapper3* allows you to use `Weka <http://www.cs.waikato.ac.nz/~ml/weka/>`_ from within Python3.

The library uses the `javabridge <https://pypi.python.org/pypi/javabridge>`_ library for starting up,
communicating with and shutting down the Java Virtual Machine in which the Weka processes get executed.

*python-weka-wrapper3* provides a thin wrapper around the basic (non-GUI) functionality of Weka (some plots are
available using Python functionality). You can automatically add all your Weka packages to the classpath.
Additional jars can be added as well.

Links:

* Looking for code?

  * `Project homepage <https://github.com/fracpete/python-weka-wrapper3>`_
  * `Example code <https://github.com/fracpete/python-weka-wrapper3-examples>`_

* Questions? You can post them in the project's `Google Group <https://groups.google.com/forum/#!forum/python-weka-wrapper>`_
* `MLOSS project <https://mloss.org/software/view/660/>`_


Requirements
============

The library has the following requirements:

* Python 3 (does not work with Python 2)

 * javabridge (>=1.0.14, required)
 * pygraphviz (optional)
 * PIL (optional)
 * matplotlib (optional)

* Oracle JDK 1.8+

Uses:

* Weka (3.9.5)

Contents
========

.. toctree::
   :maxdepth: 2

   install
   troubleshooting
   commandline
   api
   optionhandling
   virtualenv
   sourcecode
   examples
   flow

API
===

.. toctree::
   :maxdepth: 4

   weka
