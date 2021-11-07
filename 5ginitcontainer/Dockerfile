FROM python:3.6.1-alpine

# Upgrade and install basic Python dependencies.
RUN apk add --no-cache bash jq curl wget\
 && apk add --no-cache --virtual .build-deps \
        bzip2-dev \
        gcc \
        libc-dev \
  && pip install --upgrade pip setuptools \
  && pip install --no-cache-dir kubernetes==10.0.1 \
  && apk del .build-deps

RUN mkdir -p /5GOperatorInit
ADD init.py /5GOperatorInit

CMD ["/bin/bash", "-c", "cd 5GOperatorInit && python -u init.py"]

