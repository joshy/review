import logging
import psycopg2
import daiquiri.formatter
import daiquiri
from psycopg2.extras import DictCursor

from repo.app import REVIEW_DB_SETTINGS
from review.compare import diffs
from review.database import query_review_reports_development, update_metrics

daiquiri.setup(level=logging.DEBUG,
    outputs=(
        daiquiri.output.File('poll-errors.log', level=logging.ERROR),
        daiquiri.output.RotatingFile(
            'poll-debug.log',
            level=logging.DEBUG,
            # 10 MB
            max_size_bytes=10000000)
    ))


def get_review_db():
    db = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return db


def _update_metrics():
    review_db = get_review_db()
    review_cursor =  review_db.cursor(cursor_factory=DictCursor)
    rows = query_review_reports_development(review_cursor)
    count = len(rows)
    logging.debug('Iterate over total of {} rows'.format(count))
    for i, row in enumerate(rows, start=1):
        logging.debug('Iterating over row {}/{}'.format(i, count))
        logging.debug('Current jaccard_s_f: {}'.format(row['jaccard_s_f']))
        calculations = diffs(row)
        logging.debug('Row {} with new calculations: {}'.format(i,calculations[0]['jaccard']))
        update_metrics(review_cursor, row['unters_schluessel'], calculations)
        logging.debug('Updated row %s of %s', i, count)
        if (i % 10 == 0):
            review_db.commit()
    review_db.commit()
    review_cursor.close()
    logging.debug('Updating metrics done')


if __name__ == '__main__':
    _update_metrics()

