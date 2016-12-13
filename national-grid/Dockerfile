FROM orinoco:latest

COPY requirements.txt /national-grid/
RUN pip install --no-cache-dir -r /national-grid/requirements.txt
COPY national-grid.py /national-grid/
COPY utils.py /national-grid/
COPY data/places.json.geocoded /national-grid/data/

EXPOSE 8080
CMD [ "python", "/national-grid/national-grid.py" ]
