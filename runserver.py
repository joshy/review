"""
Module to run the application. Defines also logging configuration.
"""
import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('repo/settings/logging.conf')))

from repo.app import app

app.run(host='0.0.0.0', port=7777)
