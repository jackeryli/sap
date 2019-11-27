FROM python:3.7

WORKDIR /illegal-parking

COPY ./IllegalParkingDetector.py .
COPY ./requirements.txt .


RUN pip3 install -r requirements.txt

COPY ./process_illegal_parking.py .
CMD ['/bin/bash']