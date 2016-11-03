# Tayo - Live buses

This is the TfL live-buses service, exposing a websocket that can be consumed by the Quartic platform.

## Running locally

    # Set up Python3 virtualenv first
    pip install -r requirements.txt
    python tayo.py

## Building

    ./gradlew docker
