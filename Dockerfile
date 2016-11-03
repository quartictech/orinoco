FROM python:3.5.2

RUN apt-get update && apt-get install -y libgeos-dev

COPY requirements.txt /tayo/
RUN pip install --no-cache-dir -r /tayo/requirements.txt
COPY tayo.py /tayo/

EXPOSE 5000
CMD [ "python", "/tayo/tayo.py" ]
