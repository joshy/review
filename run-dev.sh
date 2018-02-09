#!/bin/sh
nodemon -e py --ignore notebooks --ignore logs --exec "python" runserver.py
