import logging
import cx_Oracle


def query_fall_id(cursor, accession_number):
    sql = """
        SELECT DISTINCT
            FALL_FREMD_ID, UNTERS_SCHLUESSEL
        FROM
            A_ABRFALL_LEISTUNG
        WHERE
            UNTERS_SCHLUESSEL = :accession_number
          """
    try:
        cursor.execute(sql, accession_number=accession_number)
        row = cursor.fetchone()
        if row is None:
            return None
        else:
            return {"fallid": row[0], "accession_number": row[1]}
    except cx_Oracle.DatabaseError as e:
        logging.error("Database error occured")
        logging.error(e)
        return None


def query_acc(cursor, befund_id):
    sql = """
        SELECT DISTINCT
            BEFUND_SCHLUESSEL, UNTERS_SCHLUESSEL
        FROM
            A_BEFUND
        WHERE
            BEFUND_SCHLUESSEL = :befund_id
          """
    try:
        cursor.execute(sql, befund_id=befund_id)
        row = cursor.fetchone()
        if row is None:
            return None
        else:
            return {"befund_id": row[0], "accession_number": row[1]}
    except cx_Oracle.DatabaseError as e:
        logging.error("Database error occured")
        logging.error(e)
        return None