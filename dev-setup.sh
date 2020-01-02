#!/bin/sh

pip3 install -r requirements.txt -r requirements-dev.txt --user
pre-commit install
pre-commit autoupdate
chmod a+x ./update_tracker.py
