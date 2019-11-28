FROM python:3.7-slim

WORKDIR /app

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt && rm requirements.txt

COPY . /app

EXPOSE 5001

ENTRYPOINT ["sh","start.sh"]

