FROM python:3.7-slim

WORKDIR /collector

RUN \
	apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt && rm ./requirements.txt

COPY ./collect_to_pulsar.py .


CMD ['/bin/bash']

