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
# Copyright (C) 2014-2016 Fracpete (pythonwekawrapper at gmail dot com)

import os
from setuptools import setup
from urllib.request import urlopen, URLError, HTTPError


def download_file(url, outfile):
    """
    Downloads the file associated with the URL and saves it to the specified output file.
    Taken from here: http://stackoverflow.com/a/4028894
    :param url: the URL to download
    :type url: str
    :param outfile: the name of the output file
    :type outfile: str
    :returns: whether the download was successful
    :rtype: bool
    """
    try:
        # Open the url
        f = urlopen(url)
        print("Downloading '" + url + "' to '" + outfile + "'")
        # Open our local file for writing
        with open(outfile, "wb") as local_file:
            local_file.write(f.read())
    # handle errors
    except HTTPError as e:
        print("HTTP Error: " + str(e.code) + " " + url)
        return False
    except URLError as e:
        print("URL Error: " + str(e.reason) + " " + url)
        return False
    return True


def download_weka():
    """
    Downloads the Weka jar from github associated with this release if nececssary.
    """
    url = "https://github.com/fracpete/python-weka-wrapper3/raw/3bada2f1c2f2874486542821fe29c9c221d65511/python/weka/lib/weka.jar"
    outfile = os.path.join(os.path.dirname(__file__), "python", "weka", "lib", "weka.jar")
    if not os.path.exists(outfile):
        if not download_file(url, outfile):
            print("Failed to download Weka jar '" + url + "' to '" + outfile + "'!")
        else:
            print("Download of Weka jar successful!")


def ext_modules():
    """
    Initiates Weka jar download.
    """
    download_weka()


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
    version="0.1.1",
    author='Peter "fracpete" Reutemann',
    author_email='pythonwekawrapper at gmail dot com',
    install_requires=[
        "javabridge>=1.0.14",
        "numpy"
    ],
    extras_require={
        'plots': ["matplotlib"],
        'graphs': ["pygraphviz", "PIL"],
    },
    ext_modules=ext_modules(),
)
