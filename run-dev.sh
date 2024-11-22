#!/bin/sh
echo "Running dev server on port 5555"
flask --app "runserver:app" --debug run --host 0.0.0.0 --port 5555