FROM python:3.5.2-alpine

COPY requirements.txt /tracker/
RUN pip install --no-cache-dir -r /tracker/requirements.txt
COPY *.py /tracker/

EXPOSE 8080
CMD [ "python", "/tracker/tracker.py" ]
