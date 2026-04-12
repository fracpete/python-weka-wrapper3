FROM ubuntu:24.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y libglib2.0-0 libsm6 libxrender-dev libxext6 libgl1 libglx-mesa0 libpq-dev libopenblas-dev git wget && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential python3-dev python3-venv python3-pip && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y graphviz libgraphviz-dev && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-21-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64/

RUN python3 -m venv --system-site-packages /opt/pww3 && \
    /opt/pww3/bin/pip --no-cache-dir install setuptools wheel && \
    /opt/pww3/bin/pip --no-cache-dir install python_weka_wrapper3[graphs,plots]==0.3.3

COPY bash.bashrc /etc/bash.bashrc

ENV WEKA_HOME=/workspace/wekafiles
ENV PATH=/opt/pww3/bin:$PATH
WORKDIR /workspace
RUN chmod 777 /workspace
