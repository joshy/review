#!/bin/sh
echo "Running dev server on port 8443"
flask --app "review.app:app" --debug run --host 0.0.0.0 --port 8443