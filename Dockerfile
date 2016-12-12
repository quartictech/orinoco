FROM python:3.6.0rc1

RUN apt-get update && apt-get install -y libgeos-dev

COPY requirements.txt /tayo/
RUN pip install --no-cache-dir -r /tayo/requirements.txt
COPY tayo.py /tayo/

EXPOSE 8080
CMD [ "python", "/tayo/tayo.py" ]
