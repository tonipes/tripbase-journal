FROM python:latest
MAINTAINER Toni Pesola

ADD /journal/requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

WORKDIR /journal
