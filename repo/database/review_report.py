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


def query_review_reports(cursor, day, writer, reviewer, report_status):
    """
    Query all reports in the review db by day and writer (optional) and 
    reviewer (optional) and befund status (optional).
    """
    sql = """
          SELECT
            a.pid,
            a.accession_number,
            a.unters_beginn,
            a.untart_kuerzel,
            a.untart_name,
            a.schreiber,
            a.vor_signierer,
            a.fin_signierer,
            a.report_status,
            a.untart_name,
            a.jaccard_v_f,
            a.jaccard_s_f,
            a.words_added_v_f,
            a.words_deleted_v_f,
            a.modality
          FROM
            sectra_reports a
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
        sql += f" AND a.fin_signierer = '{reviewer.upper()}'"
    if report_status:
        sql += f" AND a.report_status = '{report_status.lower()}'"
    sql = template.render(other_clause=sql) 
    cursor.execute(sql, (start, end))
    desc = [d[0].lower() for d in cursor.description]
    result = [dict(zip(desc, row)) for row in cursor]
    return result
