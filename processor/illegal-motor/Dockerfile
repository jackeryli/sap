FROM python:3.7

WORKDIR /motor_detection

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./camera1.ini .
COPY ./illegalMotorDetector.py .
COPY ./process_illegal_motor.py .

