FROM python:alpine

RUN apk add --update build-base openssl-dev libffi-dev linux-headers && \
    rm -rf /var/cache/apk/*

WORKDIR /work

ADD requirements.txt /work/
RUN pip install -r requirements.txt

ADD . /work/
RUN pip install -e /work/
