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
from repo.database.report import query_report_by_befund_status
from review.app import REVIEW_DB_SETTINGS, RIS_DB_SETTINGS
from review.compare import diffs
from review.database import (insert, query_review_reports, update,
                             update_metrics)

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


def query_ris(befund_status="s", hours=3):
    logger.info(f"Querying ris for befund_status {befund_status}")
    con = get_ris_db()
    start_date = datetime.now() - timedelta(hours)
    end_date = datetime.now()
    logger.debug(
        f"Query param: start date: '{start_date}', end date: '{end_date}', befund_status: '{befund_status}'"
    )

    rows = query_report_by_befund_status(
        con.cursor(), start_date, end_date, befund_status
    )
    logger.info(
        f"Querying ris for befund_status {befund_status} returned {len(rows)} rows"
    )
    con.close()
    return rows


def insert_reviews(review_cursor, befund_status="s", hours=1):
    rows = query_ris(befund_status, hours)
    count = len(rows)
    for i, row in enumerate(rows, start=1):
        logger.debug(f"Inserting row {i}/{count} rows")
        insert(review_cursor, row, befund_status)
    logger.info(f"Inserting {count} rows done")


def update_reviews(review_cursor, befund_status="l", hours=2):
    rows = query_ris(befund_status, hours)
    count = len(rows)
    logger.debug(f"Updating total of {count} rows with befund_status {befund_status}")
    for i, row in enumerate(rows, start=1):
        logger.debug(f"Updating row {i}/{count} rows")
        update(review_cursor, row, befund_status)
    logger.info(f"Updating befund_status {befund_status} done")


def calculate_comparison():
    db = get_review_db()
    cursor = db.cursor(cursor_factory=DictCursor)
    rows = query_review_reports(cursor)
    total = len(rows)
    logger.debug(f"Total rows to update {total} for metrics")
    for i, r in enumerate(rows, 1):
        d = diffs(r)
        update_metrics(cursor, r["unters_schluessel"], d)
        logger.debug(f"Updated row {i} of {total}", i, total)
        if i % 10 == 0:
            db.commit()
    db.commit()
    cursor.close()
    logger.debug(f"Updating metrics done for {total} rows")


def job():
    review_db = get_review_db()
    review_cursor = review_db.cursor()
    insert_reviews(review_cursor, hours=2)
    insert_reviews(review_cursor, "g", hours=2)
    update_reviews(review_cursor, "l", hours=2)
    update_reviews(review_cursor, "g", hours=2)
    update_reviews(review_cursor, "f", hours=2)
    review_db.commit()
    review_cursor.close()
    calculate_comparison()
    update_modalities()


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    schedule.every(5).minutes.do(job)
    t = Thread(target=run_schedule)
    t.start()
    logger.info("Polling is up and running")
