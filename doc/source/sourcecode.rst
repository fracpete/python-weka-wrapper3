Source code
===========

The following sections explain how to obtain the source code of *python-weka-wrapper*,
generate the documentation and create an installer. See also the *Troubleshooting* section.


Download
--------

You can clone the *python-weka-wrapper* repository on
`github <https://github.com/fracpete/python-weka-wrapper>`_ as follows:

.. code-block:: bash

   $ git clone https://github.com/fracpete/python-weka-wrapper.git


Documentation
-------------

Change into the directory that you created when cloning the repository and use
`sphinx-doc` to generate the documentation, e.g., `html`:

.. code-block:: bash

   $ cd python-weka-wrapper/doc
   $ make html

Use the `make` command without any parameters to check what output formats are support.


Install
-------

You can install the library as follows in the previously installed virtual environment as follows:

.. code-block:: bash

   $ /some/where/pwwtest/bin/python setup.py install
