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


def query_report(cursor, day):
    rows = _query_acccesion_number_by_day(cursor, day)
    for row in rows:
        row['rtf'] = _select_befund(cursor, row['befund_schluessel'])
    return rows


def select_report(cursor, accession_number):
    # cursor, string -> Optional[Tuple[string, Dict[str, str]]]
    """ Loads the report and the meta data. """
    logging.info('Getting accession number %s from db', accession_number)
    befund_schluessel, meta_data = _select_by_accession_number(
        cursor, accession_number)
    logging.info("Found befund schluessel %s", befund_schluessel)
    logging.info('Got meta_data %s', meta_data)
    if befund_schluessel is not None:
        return _select_befund(cursor, befund_schluessel), meta_data
    else:
        return None, None


def query_report_by_befund_status(cursor, start_date, end_date, befund_status='s'):
    rows = _query_by_befund_status(cursor, start_date, end_date, befund_status)
    for row in rows:
        column_name = 'befund_' + befund_status
        row[column_name] = _select_befund(cursor, row['befund_schluessel'])
    return rows


def _query_by_befund_status(cursor, start_date, end_date, befund_status='s'):
    """
    Query all accession number by given time range and BEFUND_STATUS.
    """
    sql = """
          SELECT
            A.PATIENT_SCHLUESSEL,
            A.UNTERS_SCHLUESSEL,
            A.UNTERS_ART,
            A.BEFUND_SCHLUESSEL,
            A.SCHREIBER,
            A.SIGNIERER,
            A.FREIGEBER,
            A.BEFUND_FREIGABE,
            A.BEFUND_STATUS,
            A.LESE_DATUM,
            A.LESER,
            A.GEGENLESE_DATUM,
            A.GEGENLESER
          FROM
            A_BEFUND A
          WHERE
              A.BEFUND_STATUS = :befund_status
            AND
              A.UNTERS_BEGINN
                BETWEEN
                  TO_DATE(:start_date, 'YYYY-MM-DD HH24:MI:SS')
                    AND
                  TO_DATE(:end_date, 'YYYY-MM-DD HH24:MI:SS')
          """
    try:
        start = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end = end_date.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(sql, start_date=start, end_date=end, befund_status=befund_status)
        desc = [d[0].lower() for d in cursor.description]
        result = [dict(zip(desc, row)) for row in cursor]
        return result
    except cx_Oracle.DatabaseError as e:
        logging.error('Database error occured')
        logging.error(e)
        return None


def _query_acccesion_number_by_day(cursor, day):
    """
    Query all accession number by day.
    """
    sql = """
          SELECT
            A.UNTERS_SCHLUESSEL,
            A.BEFUND_SCHLUESSEL,
            A.UNTERS_BEGINN,
            A.BEFUND_FREIGABE
          FROM
            A_BEFUND A
          WHERE
              BETWEEN
                TO_DATE(:start_of_day, 'YYYY-MM-DD HH24:MI:SS')
                  AND
                TO_DATE(:end_of_day, 'YYYY-MM-DD HH24:MI:SS')
          """
    try:
        start_of_day = day.strftime('%Y-%m-%d 00:00:00')
        end_of_day = day.strftime('%Y-%m-%d 23:59:59')
        cursor.execute(sql, start_of_day=start_of_day, end_of_day=end_of_day)
        desc = [d[0].lower() for d in cursor.description]
        result = [dict(zip(desc, row)) for row in cursor]
        return result
    except cx_Oracle.DatabaseError as e:
        logging.error('Database error occured')
        logging.error(e)
        return None


def _select_by_accession_number(cursor, accession_number):
    # cursor, string -> Optional[Tuple[str, Dict[str, str]]]
    """
    Loads the report from the database and also some meta data.
    The meta data is returned as a dictionary and contains informations
    such as "StudyDate".
    """
    sql = """
          SELECT
            A.BEFUND_SCHLUESSEL, A.UNTERS_BEGINN, A.BEFUND_STATUS
          FROM
            A_BEFUND A
          WHERE
            A.UNTERS_SCHLUESSEL = :accession_number
          """
    try:
        cursor.execute(sql, accession_number=accession_number)
        row = cursor.fetchone()
        if row is None:
            return None, None
        else:
            meta_data = {
                'StudyDate': row[1].strftime('%d.%m.%Y %H:%M:%S'),
                'BefundStatus': row[2]
            }
            return row[0], meta_data if row is not None else None
    except cx_Oracle.DatabaseError as e:
        logging.error('Database error occured')
        logging.error(e)
        return None, None


def _select_befund(cursor, befund_schluessel):
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