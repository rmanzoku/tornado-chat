FROM ubuntu:trusty
MAINTAINER manzoku@mobcast.jp

RUN apt-get update
RUN apt-get install -y python-setuptools
RUN easy_install pip

RUN mkdir /code
WORKDIR /code

ENV PYTHONPATH /usr/local/lib/python2.7/site-packages

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

