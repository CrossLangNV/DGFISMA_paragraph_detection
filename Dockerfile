FROM ubuntu:18.04
#gpu
#FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

MAINTAINER arne <arnedefauw@gmail.com>

ARG TYPESYSTEM_PATH

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
 && rm -rf /var/lib/apt/lists/*

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh
RUN bash Miniconda3-py37_4.8.2-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-py37_4.8.2-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

RUN conda install -y python=3.7.3 && \
conda install flask==1.1.1 

#Install Cython
RUN apt-get update
RUN apt-get -y install --reinstall build-essential
RUN apt-get -y install gcc
RUN pip install Cython

RUN pip install bs4==0.0.1 beautifulsoup4==4.5.3 dkpro-cassis==0.3.0 pexpect ipython jupyter jupyterlab pytest

WORKDIR /work
COPY app.py /work
COPY src/*.py /work/src/

COPY $TYPESYSTEM_PATH /work/typesystems/typesystem.xml

CMD python /work/app.py
