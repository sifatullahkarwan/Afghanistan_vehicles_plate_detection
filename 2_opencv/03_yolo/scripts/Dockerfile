FROM python:3.11-slim

RUN mkdir app
WORKDIR /app

COPY ./requirements.txt /app


RUN pip3 install  -r requirements.txt

COPY  .  /app/

CMD ['python3','gray.py']

#  docker build -t sifatullahkhan493/afg_number_plt .