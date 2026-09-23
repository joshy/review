import logging
import os

import psycopg2
from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

# this logger works
log = logging.getLogger("review.app")


def _env(key, default=""):
    value = os.getenv(key, default)
    if value is None:
        return default
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return value


def _enabled(key, default="false"):
    return _env(key, default).lower() in ("true", "1", "yes")


def mssql_enabled():
    """True only when mssql_db_enabled is specifically true. Default is PostgreSQL."""
    return _enabled("mssql_db_enabled", "false")


def _login_expr(column):
    if mssql_enabled():
        lowered = f"LOWER({column})"
        return f"LEFT({lowered}, CHARINDEX('@', {lowered} + '@') - 1)"
    return f"split_part(lower({column}), '@', 1)"


def _limit(count_sql):
    if mssql_enabled():
        return f"OFFSET 0 ROWS FETCH NEXT {count_sql} ROWS ONLY"
    return f"LIMIT {count_sql}"


def _modality_clause(modalities):
    modalities = list(modalities or [])
    if mssql_enabled():
        if not modalities:
            return "1 = 0", []
        marks = ", ".join(["%s"] * len(modalities))
        return f"a.modality IN ({marks})", modalities
    return "a.modality = ANY(%s)", [modalities]


def _db_errors():
    errors = [psycopg2.Error]
    try:
        import pymssql

        errors.append(pymssql.Error)
    except ImportError:
        pass
    return tuple(errors)


class _MssqlCursor:
    def __init__(self, cursor, as_dict):
        self._cursor = cursor
        self._as_dict = as_dict

    def execute(self, sql, params=None):
        if params is None:
            return self._cursor.execute(sql)
        return self._cursor.execute(sql, params)

    def _adapt(self, row):
        if row is None or not self._as_dict:
            return row
        return {str(key).lower(): value for key, value in row.items()}

    def fetchall(self):
        return [self._adapt(row) for row in self._cursor.fetchall()]

    def fetchone(self):
        return self._adapt(self._cursor.fetchone())

    def __iter__(self):
        for row in self._cursor:
            yield self._adapt(row)

    def close(self):
        return self._cursor.close()

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return self._cursor.rowcount


class _MssqlConnection:
    def __init__(self, raw):
        self._raw = raw

    def cursor(self, cursor_factory=None, **kwargs):
        as_dict = cursor_factory is not None
        return _MssqlCursor(self._raw.cursor(as_dict=as_dict), as_dict)

    def commit(self):
        return self._raw.commit()

    def rollback(self):
        return self._raw.rollback()

    def close(self):
        return self._raw.close()


def connect_review_db():
    """PostgreSQL unless mssql_db_enabled is true."""
    if not mssql_enabled():
        connection = psycopg2.connect(
            dbname=_env("REVIEW_DB_NAME"),
            user=_env("REVIEW_DB_USER"),
            password=_env("REVIEW_DB_PASSWORD"),
            host=_env("REVIEW_DB_HOST"),
            port=_env("REVIEW_DB_PORT"),
        )
        log.info(
            "Using PostgreSQL %s@%s:%s",
            _env("REVIEW_DB_NAME"),
            _env("REVIEW_DB_HOST"),
            _env("REVIEW_DB_PORT"),
        )
        return connection

    import pymssql

    connection = pymssql.connect(
        server=_env("mssql_db_host"),
        port=int(_env("mssql_db_port")),
        user=_env("mssql_db_user"),
        password=_env("mssql_db_password"),
        database=_env("mssql_db_name"),
        autocommit=True,
    )
    log.info(
        "Using MS SQL %s@%s:%s",
        _env("mssql_db_name"),
        _env("mssql_db_host"),
        _env("mssql_db_port"),
    )
    return _MssqlConnection(connection)


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


def query_report_for_hedging(cursor, bulk):
    """
    Returns the rows where the reports are finalized and hedging counts are not yet
    calculated.
    """
    sql = f"""
          SELECT
            a.accession_number,
            a.report_s,
            a.report_v,
            a.report_f,
            unters_beginn
          FROM
            sectra_reports a
          WHERE
            report_f is not null
          AND
            hedging_count_f = -1
          ORDER BY
            unters_beginn desc
          {_limit(int(bulk))}
          """
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


def query_review_report(cursor):
    """
    Returns the rows where the reports are finalized and metrics are not yet
    calculated.
    """
    sql = f"""
          SELECT
            a.accession_number,
            a.report_s,
            a.report_v,
            a.report_f,
            unters_beginn
          FROM
            sectra_reports a
          WHERE
            report_f is not null
          AND
            jaccard_s_f is null
          ORDER BY
            unters_beginn desc
          {_limit(1000)}
          """
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


def query_review_reports(cursor, day, writer, reviewer, report_status):
    """
    Query all reports in the review db by day and writer (optional) and
    reviewer (optional) and befund status (optional).
    """
    schreiber = _login_expr("a.schreiber")
    vor = _login_expr("a.vor_signierer")
    fin = _login_expr("a.fin_signierer")
    sql = f"""
          SELECT
            a.pid,
            a.accession_number,
            a.unters_beginn,
            a.untart_kuerzel,
            a.untart_name,
            {schreiber} as schreiber,
            {vor} as vor_signierer,
            {fin} as fin_signierer,
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
            {{{{ other_clause }}}}
          ORDER BY
              a.unters_beginn desc
          """
    start = day.strftime("%Y-%m-%d 00:00:00")
    end = day.strftime("%Y-%m-%d 23:59:59")
    template = Template(sql)
    sql = ""
    if writer:
        sql += f" AND {schreiber} LIKE '{writer.lower()}'"
    if reviewer:
        sql += f" AND {fin} LIKE '{reviewer.lower()}'"
    if report_status:
        sql += f" AND a.report_status = '{report_status.upper()}'"

    sql = template.render(other_clause=sql)
    cursor.execute(sql, (start, end))
    desc = [d[0].lower() for d in cursor.description]
    result = [dict(zip(desc, row)) for row in cursor]
    return result


def update_hedging(cursor, accession_number, heding_counts):
    sql = """
          UPDATE sectra_reports SET
            hedging_count_s = %s,
            hedging_count_v = %s,
            hedging_count_f = %s
          WHERE
            accession_number = %s
          """
    try:
        cursor.execute(
            sql,
            (
                heding_counts["hedging_count_s"],
                heding_counts["hedging_count_v"],
                heding_counts["hedging_count_f"],
                accession_number,
            ),
        )
        logging.info(f"Updated row for acc: {accession_number}")
    except _db_errors() as e:
        logging.error("Error %s", e)


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
    except _db_errors() as e:
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
    schreiber = _login_expr("a.schreiber")
    vor = _login_expr("a.vor_signierer")
    fin = _login_expr("a.fin_signierer")
    modality_sql, modality_params = _modality_clause(modalities)
    sql = f"""
          SELECT
            a.pid,
            a.accession_number,
            a.untart_kuerzel, 
            a.untart_name,
            a.unters_beginn,
            {schreiber} as schreiber,
            {vor} as vor_signierer,
            {fin} as fin_signierer,
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
              {schreiber} LIKE %s
          AND
              a.report_status = 'F'
          AND
              {schreiber} != {_login_expr("b.fin_signierer")}
          AND 
              {modality_sql}
          ORDER BY
              a.unters_beginn desc
          {_limit("%s")}
          """
    cursor.execute(sql, (writer, *modality_params, last_exams))
    return cursor.fetchall()


def query_by_writer_and_date_and_modality(
    cursor, writer, start_date, end_date, modalities
):
    """
    Query all reports in the review db by writer.
    """
    schreiber = _login_expr("a.schreiber")
    vor = _login_expr("a.vor_signierer")
    fin = _login_expr("a.fin_signierer")
    modality_sql, modality_params = _modality_clause(modalities)
    if mssql_enabled():
        writer_sql = f"LOWER(a.schreiber) LIKE %s"
        writer_param = f"%{writer.lower()}%"
    else:
        writer_sql = "lower(a.schreiber) LIKE '%s%'"
        writer_param = writer.lower()
    sql = f"""
          SELECT
            a.pid,
            a.accession_number,
            a.unters_beginn,
            {schreiber} as schreiber,
            {vor} as vor_signierer,
            {fin} as fin_signierer,
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
              {writer_sql}
          AND
              a.unters_beginn between %s and %s
          AND
              a.report_status = 'F'
          AND
              {modality_sql}
          ORDER BY
              a.unters_beginn desc
          """
    cursor.execute(sql, (writer_param, start_date, end_date, *modality_params))
    return cursor.fetchall()


def query_by_reviewer_and_modality(cursor, reviewer, last_exams, modalities):
    """
    Query all reports in the review db by reviewer.
    """
    schreiber = _login_expr("a.schreiber")
    vor = _login_expr("a.vor_signierer")
    fin = _login_expr("a.fin_signierer")
    modality_sql, modality_params = _modality_clause(modalities)
    sql = f"""
          SELECT
            a.pid,
            a.accession_number,
            a.unters_beginn,
            {schreiber} as schreiber,
            {vor} as vor_signierer,
            {fin} as fin_signierer,
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
              {fin} LIKE %s
          AND
              a.report_status = 'F'
          AND 
              {modality_sql}
          ORDER BY
              a.unters_beginn desc
          {_limit("%s")}
          """
    cursor.execute(sql, (reviewer.lower(), *modality_params, last_exams))
    return cursor.fetchall()


def query_all_by_departments(cursor):
    """
    Query all reports in the review db which have status final
    """
    sql = f"""
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
          {_limit(2000)}
          """
    cursor.execute(sql)
    return cursor.fetchall()


def query_by_reviewer_and_date_and_modality(
    cursor, reviewer, start_date, end_date, modalities
):
    """
    Query all reports in the review db by reviewer, date and department.
    """
    schreiber = _login_expr("a.schreiber")
    vor = _login_expr("a.vor_signierer")
    fin = _login_expr("a.fin_signierer")
    modality_sql, modality_params = _modality_clause(modalities)
    sql = f"""
          SELECT
            a.pid,
            a.accession_number,
            a.unters_beginn,
            {schreiber} as schreiber,
            {vor} as vor_signierer,
            {fin} as fin_signierer,
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
          INNER JOIN 
            sectra_reports b 
          ON 
            a.accession_number = b.accession_number
          WHERE
              {fin} LIKE %s
          AND
              a.unters_beginn between %s and %s
          AND
              a.report_status = 'F'
          AND
              a.schreiber != b.fin_signierer
          AND
              {modality_sql}
          ORDER BY
              a.unters_beginn desc
          """
    cursor.execute(sql, (reviewer.lower(), start_date, end_date, *modality_params))
    return cursor.fetchall()
