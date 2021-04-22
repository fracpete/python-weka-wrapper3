# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# setup.py
# Copyright (C) 2014-2021 Fracpete (pythonwekawrapper at gmail dot com)

from setuptools import setup


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="python-weka-wrapper3",
    description="Python3 wrapper for the Weka Machine Learning Workbench",
    long_description=(
        _read('DESCRIPTION.rst') + b'\n' +
        _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/fracpete/python-weka-wrapper3",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
    ],
    license='GNU General Public License version 3.0 (GPLv3)',
    package_dir={
        '': 'python'
    },
    packages=[
        "weka",
        "weka.core",
        "weka.flow",
        "weka.plot"
    ],
    package_data={
        "weka": ["lib/*.jar"],
    },
    include_package_data=True,
    version="0.2.2",
    author='Peter "fracpete" Reutemann',
    author_email='pythonwekawrapper@gmail.com',
    install_requires=[
        "javabridge>=1.0.14",
        "numpy",
    ],
    extras_require={
        'plots': ["matplotlib"],
        'graphs': ["pygraphviz", "PIL"],
    },
    entry_points={
        "console_scripts": [
            "pww-associator=weka.associations:sys_main",
            "pww-attsel=weka.attribute_selection:sys_main",
            "pww-classifier=weka.classifiers:sys_main",
            "pww-clusterer=weka.clusterers:sys_main",
            "pww-datagenerator=weka.datagenerators:sys_main",
            "pww-filter=weka.filters:sys_main",
        ]
    }
)
