FROM ubuntu:18.04
#gpu
#FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

MAINTAINER arne <arnedefauw@gmail.com>

#ARG MODEL_DIR

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


#pip install git+https://github.com/ArneDefauw/dkpro-cassis@master

#WORKDIR /work
#copy code:
#COPY app.py /work
#COPY code_bert_classifier/src/*.py /work/code_bert_classifier/src/
#copy model:
#COPY $MODEL_DIR/*.pth /work/models/model.pth
#COPY $MODEL_DIR/config.json /work/models/
#COPY $MODEL_DIR/special_tokens_map.json /work/models/
#COPY $MODEL_DIR/tokenizer_config.json /work/models/
#COPY $MODEL_DIR/vocab.txt /work/models/

#CMD python /work/app.py

EXPOSE 8888

VOLUME /notebook
WORKDIR /notebook

CMD ["jupyter", "notebook", "--no-browser", "--allow-root", "--ip='0.0.0.0'"]
