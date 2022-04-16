FROM nvidia/cuda:10.2-devel-ubuntu18.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y libglib2.0-0 libsm6 libxrender-dev libxext6 libgl1-mesa-glx git wget && \
    apt-get install -y build-essential python3.8-dev python3.8-venv python3.8-distutils && \
    apt-get install -y graphviz libgraphviz-dev && \
    apt-get install -y openjdk-8-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python3.8 /tmp/get-pip.py
RUN python3.8 -m pip --no-cache-dir install numpy matplotlib pygraphviz && \
    python3.8 -m pip --no-cache-dir install python-javabridge && \
    python3.8 -m pip --no-cache-dir install python-weka-wrapper3==0.2.9

COPY bash.bashrc /etc/bash.bashrc

ENV WEKA_HOME=/workspace/wekafiles
WORKDIR /workspace
RUN chmod 777 /workspace
