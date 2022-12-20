import logging
import time
from threading import Thread

import daiquiri
import daiquiri.formatter
import psycopg2
import schedule
from psycopg2.extras import DictCursor

from review.app import REVIEW_DB_SETTINGS
from review.compare import diffs
from review.database import query_review_reports, update_metrics

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


def get_review_db():
    db = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return db


def calculate_comparison():
    db = get_review_db()
    cursor = db.cursor(cursor_factory=DictCursor)
    rows = query_review_reports(cursor)
    total = len(rows)
    logger.debug(f"Total rows to update {total} for metrics")
    for i, r in enumerate(rows, 1):
        d = diffs(r)
        if d is not None:
            update_metrics(cursor, r["accession_number"], d)
            logger.debug(f"Updated row {i} of {total}", i, total)
            if i % 10 == 0:
                db.commit()
    db.commit()
    cursor.close()
    logger.debug(f"Updating metrics done for {total} rows")


def job():
    calculate_comparison()


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    schedule.every(5).minutes.do(job)
    t = Thread(target=run_schedule)
    t.start()
    logger.info("Polling is up and running")
