FROM orinoco:latest

COPY requirements.txt /btraced-tracker/
RUN pip install --no-cache-dir -r /btraced-tracker/requirements.txt
COPY *.py /btraced-tracker/

EXPOSE 8080
CMD [ "python", "/btraced-tracker/tracker.py" ]
