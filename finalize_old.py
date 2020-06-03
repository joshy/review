import logging
import time
from datetime import datetime, timedelta
from threading import Thread

import daiquiri
import daiquiri.formatter
import psycopg2
import schedule
from psycopg2.extras import DictCursor
from scripts.populate_modalities import update_modalities

from repo.database.connection import open_connection
from repo.database.report import query_report_by_befund_status, query_final_reports
from review.app import REVIEW_DB_SETTINGS, RIS_DB_SETTINGS
from review.compare import diffs
from review.database import (insert, query_review_reports, update,
                             update_metrics, query_not_finalized)

"""
Finalize old report in status 'g' which never received a status 'f'
"""

daiquiri.setup(
    level=logging.INFO,
    outputs=(
        daiquiri.output.Stream(
            formatter=daiquiri.formatter.ColorFormatter(
                fmt="%(color)s%(levelname)-8.8s " "%(name)s: %(message)s%(color_stop)s"
            )
        ),
    ),
)
logger = daiquiri.getLogger("poll")


def get_ris_db():
    db = open_connection(**RIS_DB_SETTINGS)
    return db


def get_review_db():
    db = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return db


def finalize_reviews(review_cursor):
    rows = query_not_finalized(review_cursor)
    count = len(rows)
    print(f"Total rows to be updated: {count}")
    con = get_ris_db()
    for i,row in enumerate(rows, start=1):
        ris_row = query_final_reports(con.cursor(), row[0])
        if ris_row:
            update(review_cursor, ris_row[0], "f")
            print(f"Updated finalized report {i}/{count} rows")


def job():
    review_db = get_review_db()
    review_cursor = review_db.cursor()
    finalize_reviews(review_cursor)
    review_db.commit()
    review_cursor.close()
    #calculate_comparison()
    #update_modalities()



if __name__ == "__main__":
    job()