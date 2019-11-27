FROM python:3.7

WORKDIR /people_counting

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./PeopleCountingDetector.py .
COPY ./process_people_counting.py .

COPY ./camera8.ini .
COPY ./camera1.ini .

