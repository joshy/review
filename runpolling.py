import logging
import time
from threading import Thread

from rich.logging import RichHandler
import psycopg2
import schedule
from psycopg2.extras import DictCursor

from review.app import REVIEW_DB_SETTINGS
from review.compare import diffs, hedgings
from review.database import query_review_report, update_metrics, update_hedging

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("poll")


def get_review_db():
    db = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return db


def calculate_comparison():
    db = get_review_db()
    cursor = db.cursor(cursor_factory=DictCursor)
    rows = query_review_report(cursor)
    total = len(rows)
    logger.debug(f"Total rows to update {total} for metrics")
    for i, r in enumerate(rows, 1):
        d = diffs(r)
        h = hedgings(r)
        if d is not None:
            update_metrics(cursor, r["accession_number"], d)
            update_hedging(cursor, r["accession_number"], h)
            logger.debug(f"Updated row {i} of {total}")
            if i % 10 == 0:
                db.commit()
    db.commit()
    cursor.close()
    logger.info(f"Updating metrics done for {total} rows")


def job():
    calculate_comparison()


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    schedule.every(1).minutes.do(job)
    t = Thread(target=run_schedule)
    t.start()
    logger.info("Polling is up and running")
