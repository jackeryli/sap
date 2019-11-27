#
# Object-Detection GPU Dockerfile
# @author Yen Chun Li Chia Hsin Hsu
# v1.0.0
#
# Copyright (c) 2019 Yen Chun Li https://github.com
#

FROM ubuntu:18.04

LABEL Yen Chun Li nthucsbg@gmail.com

# working directory
WORKDIR /object-detect

# install
RUN \
	apt-get update && apt-get install -y \
	autoconf \
    automake \
	libtool \
	build-essential \
    python3 \
    python3-pip \
    libsm6 \
    libxext6 \
    libxrender-dev \
	git

COPY ./coco.data .
COPY ./darknet.py .

COPY ./yolov3-tiny.weights .
COPY ./requirements.txt .

RUN pip3 install -r requirements.txt
RUN rm ./requirements.txt

# build repo
RUN \
	git clone https://github.com/AlexeyAB/darknet.git

WORKDIR darknet/

RUN wget https://pjreddie.com/media/files/yolov3.weights
RUN wget https://pjreddie.com/media/files/yolov3-tiny.weights

RUN \
    sed -i 's/LIBSO=.*/LIBSO=1/' Makefile && \
    make

RUN cp libdarknet.so ../
COPY ./coco.data ./cfg/

COPY ./darknet.py ./
RUN rm /object-detect/darknet.py

CMD nvidia-smi -q

WORKDIR /object-detect

COPY ./process_object_detection.py .
COPY ./YoloDetector.py .

CMD ['/bin/bash']

