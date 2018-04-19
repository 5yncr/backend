FROM syncrbase:latest

WORKDIR /work

ADD requirements.txt /work
RUN pip install -r requirements.txt

ADD . /work
RUN pip install -e /work

ENV LOG_LEVEL=INFO
ENV PYTHONASYNCIODEBUG=1
