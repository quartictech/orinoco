FROM python:3.6.0rc1

RUN apt-get update && apt-get install -y libgeos-dev

COPY lib /orinoco
RUN pip install --no-cache-dir /orinoco/
