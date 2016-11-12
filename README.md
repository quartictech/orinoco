# Tracker - GPS tracker

GPS tracker service, implemented as a server for the [Btraced](http://www.btraced.com/) mobile app.

Mobile uploads should be directed at the `POST :8080/tracker` endpoint.

## Running locally

    # Set up Python3 virtualenv first
    pip install -r requirements.txt
    python tracker.py

## Building

    ./gradlew docker
