import logging
import psycopg2
from psycopg2.extras import execute_values
import datetime

def query_review_reports(cursor):
    """
    Returns the rows where the reports are finalized and metrics are not yet
    calculated.
    """
    sql = """
          SELECT
            unters_schluessel,
            befund_s,
            befund_g,
            befund_f,
            unters_beginn
          FROM
            reports
          WHERE
            befund_f is not null
          AND
            jaccard_s_f is null
          OR
            total_words_g = 0
          ORDER BY
            unters_beginn desc
          LIMIT 1000
          """
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

def update_metrics(cursor, unters_schluessel, diffs):
    sql = """
          UPDATE reports SET
            jaccard_s_f = %s,
            words_added_s_f = %s,
            words_deleted_s_f = %s,
            jaccard_g_f = %s,
            words_added_g_f = %s,
            words_deleted_g_f = %s,
            total_words_s = %s,
            total_words_g = %s,
            total_words_f = %s
          WHERE
            unters_schluessel = %s
          """
    try:

        cursor.execute(sql,
          (diffs[0]['jaccard'],
           diffs[0]['additions'],
           diffs[0]['deletions'],
           diffs[1]['jaccard'],
           diffs[1]['additions'],
           diffs[1]['deletions'],
           diffs[2]['total_words_s'],
           diffs[2]['total_words_g'],
           diffs[2]['total_words_f'],
           unters_schluessel))
    except psycopg2.Error as e:
        logging.error('Error %s', e)

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


def query_by_writer(cursor, writer, last_exams):
    """
    Query all reports in the review db by writer.
    """
    sql = """
          SELECT
            a.patient_schluessel,
            a.unters_schluessel,
            a.unters_art,
            a.unters_beginn,
            a.befund_schluessel,
            a.schreiber,
            a.signierer,
            a.freigeber,
            a.befund_freigabe,
            a.befund_status,
            a.lese_datum,
            a.leser,
            a.gegenlese_datum,
            a.gegenleser,
            a.pat_name,
            a.pat_vorname,
            a.untart_name,
            a.jaccard_s_f,
            a.jaccard_g_f,
            a.words_added_s_f,
            a.words_added_g_f,
            a.words_deleted_s_f,
            a.words_deleted_g_f,
            a.total_words_s,
            a.total_words_g,
            a.total_words_f
          FROM
            reports a
          WHERE
              a.schreiber = %s
          AND
              a.befund_status = 'f'
          ORDER BY
              a.unters_beginn desc
          LIMIT %s
          """
    cursor.execute(sql, (writer.upper(), last_exams))
    return cursor.fetchall()