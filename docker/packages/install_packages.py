# helper script that is used by the Docker image to install additional packages

import weka.core.jvm as jvm
import weka.core.packages as packages

jvm.start(packages=True)

# for reproducibility, we also specify the version of the package that we need
packages.install_package("SelfOrganizingMap", version="1.0.3")

jvm.stop()
