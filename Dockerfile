FROM python:3.5.2

RUN apt-get update && apt-get install -y libgeos-dev

COPY requirements.txt /national-grid/
RUN pip install --no-cache-dir -r /national-grid/requirements.txt
COPY national-grid.py /national-grid/

EXPOSE 8080
CMD [ "python", "/national-grid/national-grid.py" ]
