import logging
import psycopg2

from jinja2 import Template


def query_review_report_by_acc(cursor, id):
    sql = """
          SELECT
            *
          FROM
            sectra_reports a
          WHERE
              a.accession_number = %s
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
            sectra_reports a
          WHERE
              a.accession_number = %s
          """
    cursor.execute(sql, (id,))
    desc = [d[0].lower() for d in cursor.description]
    result = [dict(zip(desc, row)) for row in cursor]
    return result[0] if result else []


def query_review_report(cursor):
    """
    Returns the rows where the reports are finalized and metrics are not yet
    calculated.
    """
    sql = """
          SELECT
            a.accession_number,,
            a.report_s,
            a.report_v,
            a.report_f,
            unters_beginn
          FROM
            sectra_reports
          WHERE
            report_f is not null
          AND
            jaccard_s_f is null
          OR
            (jaccard_s_f = 0 AND jaccard_v_f = 0)
          ORDER BY
            unters_beginn desc
          LIMIT 1000
          """
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


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
              a.unters_beginn desc
          """
    start = day.strftime("%Y-%m-%d 00:00:00")
    end = day.strftime("%Y-%m-%d 23:59:59")
    template = Template(sql)
    sql = ""
    if writer:
        sql += f" AND a.schreiber = '{writer.lower()}'"
    if reviewer:
        sql += f" AND a.fin_signierer = '{reviewer.lower()}'"
    if report_status:
        sql += f" AND a.report_status = '{report_status.upper()}'"

    sql = template.render(other_clause=sql)
    cursor.execute(sql, (start, end))
    desc = [d[0].lower() for d in cursor.description]
    result = [dict(zip(desc, row)) for row in cursor]
    return result


def update_metrics(cursor, accession_number, diffs):
    sql = """
          UPDATE sectra_reports SET
            jaccard_s_f = %s,
            words_added_s_f = %s,
            words_deleted_s_f = %s,
            jaccard_v_f = %s,
            words_added_v_f = %s,
            words_deleted_v_f = %s,
            total_words_s = %s,
            total_words_v = %s,
            total_words_f = %s
          WHERE
            accession_number = %s
          """
    try:

        cursor.execute(
            sql,
            (
                diffs[0]["jaccard"],
                diffs[0]["additions"],
                diffs[0]["deletions"],
                diffs[1]["jaccard"],
                diffs[1]["additions"],
                diffs[1]["deletions"],
                diffs[2]["total_words_s"],
                diffs[2]["total_words_v"],
                diffs[2]["total_words_f"],
                accession_number,
            ),
        )
    except psycopg2.Error as e:
        logging.error("Error %s", e)


def insert(cursor, row, report_status):
    field = "befund_" + report_status
    sql = f"""
          INSERT INTO reports
            (patient_schluessel,
            accession_number,
            unters_art,
            report_schluessel,
            unters_beginn,
            schreiber,
            freigeber,
            report_freigabe,
            report_status,
            report_s,
            untart_name,
            pat_name,
            pat_vorname,
            pp_misc_mfd_1_kuerzel,
            pp_misc_mfd_1_bezeichnung)
          VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          ON CONFLICT
            (accession_number)
          DO UPDATE
          SET
            {field} = %s
          """
    cursor.execute(
        sql,
        (
            row["patient_schluessel"],
            row["accession_number"],
            row["unters_art"],
            row["report_schluessel"],
            row["unters_beginn"],
            row["schreiber"],
            row["freigeber"],
            row["report_freigabe"],
            row["report_status"],
            row[field],
            row["untart_name"],
            row["pat_name"],
            row["pat_vorname"],
            row["pp_misc_mfd_1_kuerzel"],
            row["pp_misc_mfd_1_bezeichnung"],
            row[field],
        ),
    )


def query_by_writer_and_modality(cursor, writer, last_exams, modalities):
    """
    Query all reports in the review db by writer.
    """
    sql = """
          SELECT
            a.pid,
            a.accession_number,
            a.untart_kuerzel, 
            a.untart_name,
            a.unters_beginn,
            a.schreiber,
            a.vor_signierer,
            a.fin_signierer,
            a.report_status,
            a.jaccard_s_f,
            a.jaccard_v_f,
            a.words_added_s_f,
            a.words_added_v_f,
            a.words_deleted_s_f,
            a.words_deleted_v_f,
            a.total_words_s,
            a.total_words_v,
            a.total_words_f,
            a.modality
          FROM
            sectra_reports a
          INNER JOIN 
            sectra_reports b 
          ON 
            a.accession_number = b.accession_number
          WHERE
              a.schreiber = %s
          AND
              a.report_status = 'F'
          AND
              a.schreiber != b.fin_signierer
          AND 
              a.modality = ANY(%s)
          ORDER BY
              a.unters_beginn desc
          LIMIT %s
          """
    cursor.execute(sql, (writer, modalities, last_exams))
    return cursor.fetchall()


def query_by_writer_and_date_and_modality(
    cursor, writer, start_date, end_date, modalities
):
    """
    Query all reports in the review db by writer.
    """
    sql = """
          SELECT
            a.pid,
            a.accession_number,
            a.unters_beginn,
            a.schreiber,
            a.vor_signierer,
            a.fin_signierer,
            a.report_status,
            a.untart_name,
            a.jaccard_s_f,
            a.jaccard_v_f,
            a.words_added_s_f,
            a.words_added_v_f,
            a.words_deleted_s_f,
            a.words_deleted_v_f,
            a.total_words_s,
            a.total_words_v,
            a.total_words_f,
            a.modality
          FROM
            sectra_reports a 
          WHERE
              a.schreiber = %s
          AND
              a.unters_beginn between %s and %s
          AND
              a.report_status = 'F'
          AND
              a.modality = ANY(%s)
          ORDER BY
              a.unters_beginn desc
          """
    cursor.execute(sql, (writer.upper(), start_date, end_date, modalities))
    return cursor.fetchall()


def query_by_reviewer_and_modality(cursor, reviewer, last_exams, modalities):
    """
    Query all reports in the review db by reviewer.
    """
    sql = """
          SELECT
            a.pid,
            a.accession_number,
            a.unters_beginn,
            a.schreiber,
            a.vor_signierer,
            a.fin_signierer,
            a.report_status,
            a.untart_name,
            a.jaccard_s_f,
            a.jaccard_v_f,
            a.words_added_s_f,
            a.words_added_v_f,
            a.words_deleted_s_f,
            a.words_deleted_v_f,
            a.total_words_s,
            a.total_words_v,
            a.total_words_f,
            a.modality
          FROM
            sectra_reports a
          WHERE
              a.fin_signierer ilike %s
          AND
              a.report_status = 'F'
          AND 
              a.modality= ANY(%s)
          ORDER BY
              a.unters_beginn desc
          LIMIT %s
          """
    cursor.execute(sql, (reviewer.upper(), modalities, last_exams))
    return cursor.fetchall()


def query_all_by_departments(cursor):
    """
    Query all reports in the review db which have status final
    """
    sql = """
          SELECT
            a.jaccard_s_f,
            a.jaccard_v_f,
            a.words_added_s_f,
            a.words_added_v_f,
            a.words_deleted_s_f,
            a.words_deleted_v_f,
            a.total_words_s,
            a.total_words_v,
            a.total_words_f
          FROM
            sectra_reports a
          INNER JOIN 
            sectra_reports b 
          ON 
            a.accession_number = b.accession_number
          WHERE
              a.report_status = 'F'
          AND
              a.schreiber != b.fin_signierer
          ORDER BY
              a.unters_beginn desc
          LIMIT 2000
          """
    cursor.execute(sql)
    return cursor.fetchall()


def query_by_reviewer_and_date_and_modality(
    cursor, reviewer, start_date, end_date, modalities
):
    """
    Query all reports in the review db by reviewer, date and department.
    """
    sql = """
          SELECT
            a.patient_schluessel,
            a.accession_number,
            a.unters_art,
            a.unters_beginn,
            a.report_schluessel,
            a.schreiber,
            a.signierer,
            a.freigeber,
            a.report_freigabe,
            a.report_status,
            a.lese_datum,
            a.leser,
            a.gegenlese_datum,
            a.gegenleser,
            a.pat_name,
            a.pat_vorname,
            a.untart_name,
            a.jaccard_s_f,
            a.jaccard_v_f,
            a.words_added_s_f,
            a.words_added_v_f,
            a.words_deleted_s_f,
            a.words_deleted_v_f,
            a.total_words_s,
            a.total_words_v,
            a.total_words_f,
            a.pp_misc_mfd_1_kuerzel,
            a.pp_misc_mfd_1_bezeichnung,
            a.modality
          FROM
            reports a 
          INNER JOIN 
            reports b 
          ON 
            a.accession_number = b.accession_number
          WHERE
              a.freigeber = %s
          AND
              a.unters_beginn between %s and %s
          AND
              a.report_status = 'F'
          AND
              a.schreiber != b.freigeber
          AND
              a.modality = ANY(%s)
          ORDER BY
              a.unters_beginn desc
          """
    cursor.execute(sql, (reviewer.upper(), start_date, end_date, modalities))
    return cursor.fetchall()


def query_not_finalized(cursor):
    sql = """
              SELECT
                 report_schluessel
              FROM
                 sectra_reports
              WHERE
                 report_v is not NULL
              AND
                 report_f is NULL
          """
    cursor.execute(sql)
    return cursor.fetchall()
