FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y libglib2.0-0 libsm6 libxrender-dev libxext6 libgl1-mesa-glx git wget && \
    apt-get install -y build-essential python3-dev python3-venv python3-pip && \
    apt-get install -y graphviz libgraphviz-dev && \
    apt-get install -y openjdk-8-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 --no-cache-dir install numpy matplotlib pygraphviz && \
    pip3 --no-cache-dir install python-javabridge && \
    pip3 --no-cache-dir install python-weka-wrapper3==0.2.8

COPY bash.bashrc /etc/bash.bashrc

ENV WEKA_HOME=/workspace/wekafiles
WORKDIR /workspace
RUN chmod 777 /workspace
