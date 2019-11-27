FROM python:3.7

WORKDIR /traffic-flow

RUN \
	apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./process_traffic_flow.py .

CMD ['/bin/bash']