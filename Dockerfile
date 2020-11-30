FROM ubuntu:18.04
#gpu
#FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

MAINTAINER arne <arnedefauw@gmail.com>

ARG DEEPSEGMENT_MODEL_PATH
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
conda install flask==1.1.1 && \
conda install -c conda-forge spacy==2.3.2 && \
conda install -c conda-forge spacy-model-en_core_web_lg

#Install Cython
RUN apt-get update
RUN apt-get -y install --reinstall build-essential
RUN apt-get -y install gcc
RUN pip install Cython

#cpu
RUN pip install bs4==0.0.1 beautifulsoup4==4.5.3 dkpro-cassis==0.5.0 deepsegment==2.3.1 tensorflow==1.14 fasttext==0.9.2 nltk==3.5 pyspellchecker==0.5.5 langdetect==1.0.8 plac==1.2.0 ipython jupyter jupyterlab pytest && \
python -m nltk.downloader punkt

#gpu
#RUN pip install bs4==0.0.1 beautifulsoup4==4.5.3 dkpro-cassis==0.3.0 deepsegment==2.3.1 tensorflow-gpu==1.14 fasttext==0.9.2 nltk==3.5 pyspellchecker==0.5.5 langdetect==1.0.8 ipython jupyter jupyterlab pytest && \
#python -m nltk.downloader punkt


WORKDIR /work
COPY app.py /work
COPY src/*.py /work/src/

COPY $TYPESYSTEM_PATH /work/typesystems/typesystem.xml

COPY $DEEPSEGMENT_MODEL_PATH/checkpoint /work/deepsegment_model/checkpoint
COPY $DEEPSEGMENT_MODEL_PATH/params /work/deepsegment_model/params
COPY $DEEPSEGMENT_MODEL_PATH/utils /work/deepsegment_model/utils
COPY $DEEPSEGMENT_MODEL_PATH/final_weights /work/deepsegment_model/final_weights

CMD python /work/app.py
