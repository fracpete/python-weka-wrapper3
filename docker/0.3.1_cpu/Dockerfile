FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y libglib2.0-0 libsm6 libxrender-dev libxext6 libgl1-mesa-glx git wget && \
    apt-get install -y build-essential python3-dev python3-venv python3-pip && \
    apt-get install -y graphviz libgraphviz-dev && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
RUN pip3 --no-cache-dir install setuptools wheel && \
    pip3 --no-cache-dir install python-weka-wrapper3[graphs,plots]==0.3.1

COPY bash.bashrc /etc/bash.bashrc

ENV WEKA_HOME=/workspace/wekafiles
WORKDIR /workspace
RUN chmod 777 /workspace
