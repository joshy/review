import logging
import psycopg2


def query_review_reports(cursor):
    """
    Returns the rows where the reports are finalized and metrics are not yet
    calculated.
    """
    sql = """
          SELECT
            accession_number,
            report_s,
            report_v,
            report_f,
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
                diffs[2]["total_words_g"],
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


def update(cursor, row, report_status):
    field = "befund_" + report_status
    sql = """
          UPDATE reports
          SET
            {} = %s,
            lese_datum = %s,
            leser = %s,
            gegenlese_datum = %s,
            gegenleser = %s,
            freigeber = %s,
            report_status = %s,
            report_freigabe = %s,
            unters_beginn = %s,
            pat_vorname = %s,
            pat_name = %s,
            untart_name = %s
          WHERE
            accession_number = %s
          """.format(
        field
    )
    cursor.execute(
        sql,
        (
            row[field],
            row["lese_datum"],
            row["leser"],
            row["gegenlese_datum"],
            row["gegenleser"],
            row["freigeber"],
            row["report_status"],
            row["report_freigabe"],
            row["unters_beginn"],
            row["pat_vorname"],
            row["pat_name"],
            row["untart_name"],
            row["accession_number"],
        ),
    )


def query_by_writer_and_department_and_modality(
    cursor, writer, last_exams, departments, modalities
):
    print(modalities)
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
              a.report_status = 'f'
          AND
              a.schreiber != b.fin_signierer
          AND 
              a.modality = ANY(%s)
          ORDER BY
              a.unters_beginn desc
          LIMIT %s
          """
    cursor.execute(sql, (writer.upper(), modalities, last_exams))
    return cursor.fetchall()


def query_by_writer_and_date_and_department_and_modality(
    cursor, writer, start_date, end_date, departments, modalities
):
    """
    Query all reports in the review db by writer.
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
            a.jaccard_g_f,
            a.words_added_s_f,
            a.words_added_g_f,
            a.words_deleted_s_f,
            a.words_deleted_g_f,
            a.total_words_s,
            a.total_words_g,
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
              a.schreiber = %s
          AND
              a.unters_beginn between %s and %s
          AND
              a.report_status = 'f'
          AND
              a.schreiber != b.freigeber
          AND
              a.pp_misc_mfd_1_kuerzel = ANY(%s)
          AND
              a.modality = ANY(%s)
          ORDER BY
              a.unters_beginn desc
          """
    cursor.execute(sql, (writer.upper(), start_date, end_date, departments, modalities))
    return cursor.fetchall()


def query_by_reviewer_and_department_and_modality(
    cursor, reviewer, last_exams, departments, modalities
):
    """
    Query all reports in the review db by reviewer.
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
            a.jaccard_g_f,
            a.words_added_s_f,
            a.words_added_g_f,
            a.words_deleted_s_f,
            a.words_deleted_g_f,
            a.total_words_s,
            a.total_words_g,
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
              a.report_status = 'f'
          AND
              a.schreiber != b.freigeber
          AND 
              a.pp_misc_mfd_1_kuerzel = ANY(%s)
          AND 
              a.modality= ANY(%s)
          ORDER BY
              a.unters_beginn desc
          LIMIT %s
          """
    cursor.execute(sql, (reviewer.upper(), departments, modalities, last_exams))
    return cursor.fetchall()


def query_by_reviewer_and_date_and_department_and_modality(
    cursor, reviewer, start_date, end_date, departments, modalities
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
            a.jaccard_g_f,
            a.words_added_s_f,
            a.words_added_g_f,
            a.words_deleted_s_f,
            a.words_deleted_g_f,
            a.total_words_s,
            a.total_words_g,
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
              a.report_status = 'f'
          AND
              a.schreiber != b.freigeber
          AND
              a.pp_misc_mfd_1_kuerzel = ANY(%s)
          AND
              a.modality = ANY(%s)
          ORDER BY
              a.unters_beginn desc
          """
    cursor.execute(
        sql, (reviewer.upper(), start_date, end_date, departments, modalities)
    )
    return cursor.fetchall()


def query_all_by_departments(cursor, departments):
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
              a.report_status = 'f'
          AND
              a.schreiber != b.fin_signierer
          ORDER BY
              a.unters_beginn desc
          LIMIT 2000
          """
    cursor.execute(sql, [departments])
    return cursor.fetchall()


def update_department_development(cursor, row, item):
    """
    Temporary Method to fill existing rows with the department description (development)
    """
    sql = """
              UPDATE sectra_eports SET 
                pp_misc_mfd_1_kuerzel = %s
              WHERE
                accession_number = %s
              """
    cursor.execute(sql, (item, row))


def update_modality(cursor, row, item):
    """
    Temporary Method to fill existing rows with the modality description
    """
    sql = """
              UPDATE sectra_reports SET 
                modality = %s
              WHERE
                accession_number = %s
              """
    cursor.execute(sql, (item, row))


def query_all_rows(cursor):
    """
    Temporary Method: query all rows (development)
    """
    sql = """
              SELECT
                 accession_number
              FROM sectra_reports
            
               """
    cursor.execute(sql)
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
