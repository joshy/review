import cx_Oracle
import sys
import logging


def open_connection(host, port, service, user, password):
    logging.debug('Opening connection to db')
    dsn = cx_Oracle.makedsn(host, port, service)
    con = cx_Oracle.connect(user, password, dsn)
    return con


def load_report(cursor, accession_number):
    befund_schluessel = _load_by_accession_number(cursor, accession_number)
    print("Got BEFUND_SCHLUESSEL", befund_schluessel)
    return _load_befund(cursor, accession_number, befund_schluessel)


def _load_by_accession_number(cursor, accession_number):
    sql = """
          SELECT
            A.BEFUND_SCHLUESSEL
          FROM
            A_BEFUND A
          WHERE
            A.UNTERS_SCHLUESSEL = :accession_number
          """
    cursor.execute(sql, accession_number=accession_number)
    row = cursor.fetchone()
    return row[0]


def _load_befund(cursor, accession_number, befund_schluessel):
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
