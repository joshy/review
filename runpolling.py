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


def query_ris(befund_status='s', hours=3):
    logging.info("Querying ris database for befund_status {}".format(befund_status))
    con =  get_ris_db()
    start_date = datetime.now() - timedelta(hours)
    end_date = datetime.now()
    logging.debug("Query param: start date: '{}', end date: '{}', befund_status: '{}'"
        .format(start_date, end_date, befund_status))
    rows = query_report_by_befund_status(con.cursor(), start_date, end_date, befund_status)
    logging.info("Querying ris for befund_status {} returned #rows {}"
        .format(befund_status, len(rows)))
    con.close()
    return rows


def insert_reviews(review_cursor, hours=1):
    rows = query_ris('s', hours)
    count = len(rows)
    for i, row in enumerate(rows, start=1):
        logging.debug('Inserting row {}/{} rows'.format(i, count))
        insert(review_cursor, row)
    logging.info('Inserting done')


def update_reviews(review_cursor, befund_status='l', hours=2):
    rows = query_ris(befund_status, hours)
    count = len(rows)
    logging.debug('Updating total of {} rows with befund_status {}'
        .format(count, befund_status))
    for i, row in enumerate(rows, start=1):
        logging.debug('Updating row {}/{} rows'.format(i, count))
        update(review_cursor, row, befund_status)
    logging.info('Updating befund_status {} done'.format(befund_status))


def job():
    review_db = get_review_db()
    review_cursor = review_db.cursor()
    insert_reviews(review_cursor, hours=2)
    update_reviews(review_cursor, 'l', hours=2)
    update_reviews(review_cursor, 'g', hours=2)
    update_reviews(review_cursor, 'f', hours=2)
    review_db.commit()
    review_cursor.close()


def update(cursor, row, befund_status):
    field = 'befund_' + befund_status
    sql = """
          UPDATE reports
          SET
            {} = %s,
            lese_datum = %s,
            leser = %s,
            gegenlese_datum = %s,
            gegenleser = %s,
            befund_status = %s,
            befund_freigabe = %s,
            unters_beginn = %s,
            pat_vorname = %s,
            pat_name = %s,
            untart_name = %s
          WHERE
            unters_schluessel = %s
          """.format(field)
    cursor.execute(sql,
        (row[field],
        row['lese_datum'],
        row['leser'],
        row['gegenlese_datum'],
        row['gegenleser'],
        row['befund_status'],
        row['befund_freigabe'],
        row['unters_beginn'],
        row['pat_vorname'],
        row['pat_name'],
        row['untart_name'],
        row['unters_schluessel']))


def insert(cursor, row):
    sql = """
          INSERT INTO reports
            (patient_schluessel,
            unters_schluessel,
            unters_art,
            befund_schluessel,
            unters_beginn,
            schreiber,
            freigeber,
            befund_freigabe,
            befund_status,
            befund_s,
            untart_name,
            pat_name,
            pat_vorname)
          VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          ON CONFLICT
            (unters_schluessel)
          DO NOTHING
          """
    cursor.execute(sql,
        (row['patient_schluessel'],
        row['unters_schluessel'],
        row['unters_art'],
        row['befund_schluessel'],
        row['unters_beginn'],
        row['schreiber'],
        row['freigeber'],
        row['befund_freigabe'],
        row['befund_status'],
        row['befund_s'],
        row['untart_name'],
        row['pat_name'],
        row['pat_vorname']))

def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    schedule.every(30).minutes.do(job)
    t = Thread(target=run_schedule)
    t.start()
    logging.info('Polling is up and running')
