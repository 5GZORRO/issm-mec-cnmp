FROM python:3.6.5-alpine

RUN apk add --no-cache bash \
 && apk add --no-cache --virtual .build-deps \
        bzip2-dev \
        g++ \
        libc-dev

RUN pip install --upgrade pip setuptools

RUN pip install --no-cache-dir gevent==1.2.1 flask>=1.0.0 requests==2.13.0 kubernetes==10.0.1 \
  && apk del .build-deps

RUN mkdir -p /apiServer
ADD server.py /apiServer/

ADD fiveg-core.yaml /
ADD fiveg-subnet.yaml /
ADD fiveg-subnet-delete.yaml /

ADD fiveg-app.yaml /

CMD ["/bin/bash", "-c", "cd apiServer && python -u server.py"]
