# Tayo - Live buses

This is the TfL live-buses service, exposing a websocket that can be consumed by the Quartic platform.

## Running locally

**Note:** This relies on Python 3.6+ (in RC at the time of writing).

    # Install geos
    brew install geos

    # Set up Python3 virtualenv first
    pip install -r requirements.txt
    python tayo.py

## Building

    ./gradlew docker
