# Installing packages in Docker image

When building Docker images for your environments, your code will most likely rely
on additional Weka packages. You can install the packages by creating a little
Python script that uses python-weka-wrapper3 to install them (just like you would
normally do in a script). Here is the content of the [install_packages.py](install_packages.py)
script:

```python
import weka.core.jvm as jvm
import weka.core.packages as packages

jvm.start(packages=True)

# for reproducibility, we also specify the version of the package that we need
packages.install_package("SelfOrganizingMap", version="1.0.3")

jvm.stop()
```

A minimal `Dockerfile` then looks like this (using the CPU Docker base image of pww3 0.2.9):

```
FROM fracpete/pww3:0.2.9_cpu
COPY install_packages.py /workspace/install_packages.py
RUN python3 /workspace/install_packages.py
```

You can then build this image just like any other Docker image:

```bash
docker build -t pww3-pkg .
```

The following command simply runs the local [test_packages.py](test_packages.py) script
to check whether the installation was successful. To achieve this, it maps the 
current directory (``pwd``) into the container's `/workspace/scripts` directory: 

```bash
docker run \
    -v `pwd`:/workspace/scripts \
    -t pww3-pkg:latest \
    python3 /workspace/scripts/test_packages.py
```

The output will be something like this:

```
DEBUG:weka.core.jvm:Adding bundled jars
DEBUG:weka.core.jvm:Classpath=['/usr/local/lib/python3.8/dist-packages/javabridge/jars/rhino-1.7R4.jar', '/usr/local/lib/python3.8/dist-packages/javabridge/jars/runnablequeue.jar', '/usr/local/lib/python3.8/dist-packages/javabridge/jars/cpython.jar', '/usr/local/lib/python3.8/dist-packages/weka/lib/weka.jar', '/usr/local/lib/python3.8/dist-packages/weka/lib/python-weka-wrapper.jar']
DEBUG:weka.core.jvm:MaxHeapSize=default
DEBUG:weka.core.jvm:Package support enabled
SelfOrganizingMap/1.0.3
  http://prdownloads.sourceforge.net/wekann/SelfOrganizingMap1.0.3.zip?download
weka.clusterers.SelfOrganizingMap -L 1.0 -O 2000 -C 1000 -H 2 -W 2
```
