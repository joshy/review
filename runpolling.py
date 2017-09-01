import time
import logging
from datetime import datetime, timedelta
from threading import Thread
import psycopg2
import daiquiri
import daiquiri.formatter
import schedule

from repo.app import RIS_DB_SETTINGS, REVIEW_DB_SETTINGS
from repo.database.connection import open_connection
from repo.database.report import query_report_by_befund_status


daiquiri.setup(level=logging.DEBUG,
    outputs=(
        daiquiri.output.File('poll-errors.log', level=logging.ERROR),
        daiquiri.output.RotatingFile(
            'poll-debug.log',
            level=logging.DEBUG,
            # 10 MB
            max_size_bytes=10000000)
    ))


def get_ris_db():
    db = open_connection(**RIS_DB_SETTINGS)
    return db


def get_review_db():
    db = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return db


def query_ris(befund_status='s'):
    logging.info("Start querying the database")
    con =  get_ris_db()
    start_date = datetime.now() - timedelta(hours=2)
    end_date = datetime.now() - timedelta(hours=1)
    logging.debug("Start date is {} an End date is {}".format(start_date, end_date))
    rows = query_report_by_befund_status(con.cursor(), start_date, end_date, befund_status='s')
    logging.info("Query returned #rows {}".format(len(rows)))
    con.close()
    return rows


def insert_review():
    rows = query_ris()
    review_db = get_review_db()
    review_cursor = review_db.cursor()
    count = len(rows)
    for i, row in enumerate(rows):
        logging.debug('Inserting row {} of total {}'.format(i, count))
        insert(review_cursor, row)
    logging.info('Inserting done')
    review_db.commit()
    review_cursor.close()


def update_review(befund_status='l'):
    rows = query_ris(befund_status)
    review_db = get_review_db()
    review_cursor = review_db.cursor()
    for row in rows:
        update(review_cursor, row, befund_status)


def job():
    insert_review()
    update_review('l')
    update_review('g')
    update_review('f')


def update(cursor, row, befund_status):
    field = 'befund_' + befund_status
    sql = """
          UPDATE reports
          SET
            {} = %s,
            lese_datum = %s,
            leser = %s,
            gegenlese_datum = %s,
            gegenleser = %s
          WHERE
            befund_schluessel = %s
          """.format(field)
    cursor.execute(sql,
        row['befund'],
        row['lese_datum'],
        row['leser'],
        row['gegenlese_datum'],
        row['gegenleser'],
        row['befund_schluessel'])

def insert(cursor, row):
    sql = """
          INSERT INTO reports
          (patient_schluessel,
          unters_schluessel,
          unters_art,
          befund_schluessel,
          schreiber,
          freigeber,
          befund_freigabe,
          befund_status,
          befund_s)
          VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s, %s)
          """
    cursor.execute(sql,
        (row['patient_schluessel'],
        row['unters_schluessel'],
        row['unters_art'],
        row['befund_schluessel'],
        row['schreiber'],
        row['freigeber'],
        row['befund_freigabe'],
        row['befund_status'],
        row['befund_s']))

def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    schedule.every(10).seconds.do(job)
    t = Thread(target=run_schedule)
    t.start()
    logging.info('Polling is running')
