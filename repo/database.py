"""
  A visualization of the views and its relationship between.
  UNTERS_SCHLUESSEL ^= ACCESSION NUMBER

                             VIEW: A_BEFUND
  +---------------------------------------+
  |UNTERS_SCHLUESSEL |  BEFUND_SCHLUESSEL |
  +---------------------------------------+
  |                  |                    |
  +---------------------------------------+
                               |
          +--------------------+
          v                VIEW: A_BEFUND_TEXT
  +------------------------------------------+
  | BEFUND_SCHLUESSEL| SQZ     |  BEFUND_TEXT|
  +------------------------------------------+
  |                  |         |             |
  +------------------------------------------+
"""
import logging
import cx_Oracle


def open_connection(host, port, service, user, password):
    logging.debug('Opening connection to db')
    dsn = cx_Oracle.makedsn(host, port, service)
    con = cx_Oracle.connect(user, password, dsn)
    return con


def load_report(cursor, accession_number):
    logging.info('Getting accession number %s from db', accession_number)
    befund_schluessel = _load_by_accession_number(cursor, accession_number)
    logging.info("Found befund schluessel %s", befund_schluessel)
    if befund_schluessel is not None:
        return _load_befund(cursor, befund_schluessel)
    else:
        return None


def _load_by_accession_number(cursor, accession_number):
    sql = """
          SELECT
            A.BEFUND_SCHLUESSEL
          FROM
            A_BEFUND A
          WHERE
            A.UNTERS_SCHLUESSEL = :accession_number
          """
    try:
        cursor.execute(sql, accession_number=accession_number)
        row = cursor.fetchone()
        return row[0] if row is not None else None
    except cx_Oracle.DatabaseError as e:
        logging.error('Database error occured')
        logging.error(e)
        return None


def _load_befund(cursor, befund_schluessel):
    sql = """
          SELECT
            A.BEFUND_TEXT
          FROM
            A_BEFUND_TEXT A
          WHERE
            A.BEFUND_SCHLUESSEL = :befund_schluessel
          ORDER BY
            A.BEFUND_TEXT_SEQUENZ
          """
    cursor.execute(sql, befund_schluessel=str(befund_schluessel))
    result_set = cursor.fetchall()
    doc = ''.join([row[0] for row in result_set])
    return doc
