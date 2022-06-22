# script for testing the packages installed in the docker image by the "install_packages.py" script

import weka.core.jvm as jvm
import weka.core.packages as packages
from weka.clusterers import Clusterer

jvm.start(packages=True)

# list packages
items = packages.installed_packages()
for item in items:
    print(item.name + "/" + item.version + "\n  " + item.url)

# instantiate from package
cls = Clusterer(classname="weka.clusterers.SelfOrganizingMap")
print(cls.to_commandline())

jvm.stop()
