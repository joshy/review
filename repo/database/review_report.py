def query_review_reports(cursor, day):
    """
    Query all reports in the review db by day.
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
            a.gegenleser
          FROM
            reports a
          WHERE
              a.unters_beginn
                BETWEEN
                  %s
                    AND
                  %s
          ORDER BY
              a.unters_beginn
          """
    start = day.strftime('%Y-%m-%d 00:00:00')
    end = day.strftime('%Y-%m-%d 23:59:59')
    cursor.execute(sql, (start, end))
    desc = [d[0].lower() for d in cursor.description]
    result = [dict(zip(desc, row)) for row in cursor]
    return result
