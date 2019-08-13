from jinja2 import Template


def query_review_report_by_acc(cursor, id):
    sql = """
          SELECT
            *
          FROM
            reports a
          WHERE
              a.unters_schluessel = %s
          """
    cursor.execute(sql, (id,))
    desc = [d[0].lower() for d in cursor.description]
    result = [dict(zip(desc, row)) for row in cursor]
    return result[0] if result else []


def query_review_report(cursor, id):
    sql = """
          SELECT
            *
          FROM
            reports a
          WHERE
              a.befund_schluessel = %s
          """
    cursor.execute(sql, (id,))
    desc = [d[0].lower() for d in cursor.description]
    result = [dict(zip(desc, row)) for row in cursor]
    return result[0] if result else []


def query_review_reports(cursor, day, writer, reviewer, befund_status):
    """
    Query all reports in the review db by day and writer (optional) and 
    reviewer (optional) and befund status (optional).
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
            a.jaccard_g_f,
            a.jaccard_s_f,
            a.words_added_g_f,
            a.words_deleted_g_f,
            a.pp_misc_mfd_1_kuerzel,
            a.pp_misc_mfd_1_bezeichnung,
            a.modality
          FROM
            reports a
          WHERE
              a.unters_beginn
                BETWEEN
                  %s
                    AND
                  %s
            {{ other_clause }}
          ORDER BY
              a.unters_beginn
          """
    start = day.strftime("%Y-%m-%d 00:00:00")
    end = day.strftime("%Y-%m-%d 23:59:59")
    template = Template(sql)
    sql = ""
    if writer:
        sql += f" AND a.schreiber = '{writer.upper()}'"
    if reviewer:
        sql += f" AND a.freigeber = '{reviewer.upper()}'"
    if befund_status:
        sql += f" AND a.befund_status = '{befund_status.lower()}'"
    sql = template.render(other_clause=sql) 
    cursor.execute(sql, (start, end))
    desc = [d[0].lower() for d in cursor.description]
    result = [dict(zip(desc, row)) for row in cursor]
    return result
