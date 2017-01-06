FROM orinoco:latest

COPY requirements.txt /mock-tracker/
RUN pip install --no-cache-dir -r /mock-tracker/requirements.txt
COPY *.py /mock-tracker/

EXPOSE 8080
CMD [ "python", "/mock-tracker/mock-tracker.py" ]
