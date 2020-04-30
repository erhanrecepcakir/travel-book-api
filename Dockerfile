FROM python:3.7-alpine
MAINTAINER erhanrecepcakir

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /tbapp
WORKDIR /tbapp
COPY ./tbapp /tbapp

RUN adduser -D user
USER user
