#!/usr/bin/env bash
source env/bin/activate
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=test.py
flask run
