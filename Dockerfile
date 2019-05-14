FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 LANGUAGE=en_US.UTF-8
   
RUN apt-get update && apt-get -y install \
    build-essential \
    git-core \
    pkg-config \
    python3-pip \
    python3-tk \
    python3 \
    python3-dev

RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Configure Jupyter notebook to produce Python code each time a notebook is saved
COPY docker_auxiliary docker_auxiliary
RUN jupyter notebook --generate-config && \
    cat docker_auxiliary/jupyter_config_part.txt ~/.jupyter/jupyter_notebook_config.py > config_concatenated.py && \
    mv config_concatenated.py ~/.jupyter/jupyter_notebook_config.py
