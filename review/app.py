import logging
import os
from datetime import datetime

import pandas as pd
import psycopg2
from flask import Flask, g, jsonify, make_response, render_template, request
from flask_assets import Bundle, Environment
from psycopg2.extras import RealDictCursor


from repo.converter import rtf_to_text
from repo.database.connection import open_connection

from repo.database.review_report import (
    query_review_report,
    query_review_reports,
    query_review_report_by_acc,
)

from review.calculations import (
    calculate_median,
    calculate_median_by_reviewer,
    calculate_median_by_writer,
    relative,
)
from review.database import (
    query_all_by_departments,
    query_by_reviewer_and_date_and_department_and_modality,
    query_by_reviewer_and_department_and_modality,
    query_by_writer_and_date_and_department_and_modality,
    query_by_writer_and_department_and_modality,
)

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("repo.default_config")
app.config.from_pyfile("config.cfg")
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.jinja_env.add_extension("jinja2.ext.do")
version = app.config["VERSION"] = "3.2.7"

RIS_DB_SETTINGS = {
    "host": app.config["RIS_DB_HOST"],
    "port": app.config["RIS_DB_PORT"],
    "service": app.config["RIS_DB_SERVICE"],
    "user": app.config["RIS_DB_USER"],
    "password": app.config["RIS_DB_PASSWORD"],
}

REVIEW_DB_SETTINGS = {
    "dbname": app.config["REVIEW_DB_NAME"],
    "user": app.config["REVIEW_DB_USER"],
    "password": app.config["REVIEW_DB_PASSWORD"],
    "host": app.config["REVIEW_DB_HOST"],
    "port": app.config["REVIEW_DB_PORT"],
}

REPORTS_FOLDER = "reports"
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

assets = Environment(app)
js = Bundle(
    "js/plugins/jquery-3.1.0.min.js",
    "js/plugins/moment.min.js",
    "js/plugins/pikaday.js",
    "js/plugins/pikaday.jquery.js",
    "js/dashboard/writerDashboard.js",
    "js/dashboard/reviewerDashboard.js",
    "js/handlers/diffHandling.js",
    "js/handlers/checkBoxHandling.js",
    "js/handlers/datePickerHandling.js",
    "js/handlers/clearHandling.js",
    "js/handlers/infoHandling.js",
    "js/handlers/buttonHandling.js",
    "js/handlers/floatTheadHandling.js",
    "js/graphs/graph.js",
    "js/graphs/pieChart.js",
    "js/graphs/barChart.js",
    filters="jsmin",
    output="gen/packed.js",
)
assets.register("js_all", js)


@app.route("/")
def review():
    now = datetime.now().strftime("%d.%m.%Y")
    day = request.args.get("day", now)
    writer = request.args.get("writer", "")
    reviewer = request.args.get("reviewer", "")
    dd = datetime.strptime(day, "%d.%m.%Y")
    con = get_review_db()
    rows = query_review_reports(con.cursor(), dd, writer, reviewer)
    day = dd.strftime("%d.%m.%Y")
    return render_template(
        "review.html",
        rows=rows,
        day=day,
        writer=writer,
        reviewer=reviewer,
        version=version,
    )


@app.route("/diff/<id>")
def diff(id):
    con = get_review_db()
    row = query_review_report(con.cursor(), id)
    cases = ["befund_s", "befund_g", "befund_f"]
    for c in cases:
        if c in row:
            field = c + "_text"
            v = row[c]
            if v:
                row[field] = rtf_to_text(v)
    return render_template("diff.html", row=row, version=version)


@app.route("/diff")
def diff_by_accession():
    con = get_review_db()
    acc = request.args.get("accession_number", -1)
    row = query_review_report_by_acc(con.cursor(), acc)
    cases = ["befund_s", "befund_g", "befund_f"]
    for c in cases:
        if c in row:
            field = c + "_text"
            v = row[c]
            if v:
                row[field] = rtf_to_text(v)
    return render_template("diff.html", row=row, version=version)


@app.route("/writer-dashboard")
def writer_dashboard():
    writer = request.args.get("w", "")
    last_exams = request.args.get("last_exams", 30)
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    departments = request.args.getlist("departments") or [
        "AOD",
        "CTD",
        "MSK",
        "NUK",
        "IR",
        "FPS",
        "MAM",
        "NR",
        "UKBB",
    ]
    departments = "{" + ",".join(departments) + "}"
    modalities = request.args.getlist("modalities") or [
        "CT",
        "MRI",
        "US",
        "RX",
        "OTHER",
    ]
    modalities = "{" + ",".join(modalities) + "}"
    rows = load_data_by_writer(
        writer, last_exams, start_date, end_date, departments, modalities
    )
    df_rows = pd.DataFrame(rows)
    df_rows = relative(df_rows)
    df_rows = remove_NaT_format(df_rows)
    data = calculate_median_by_reviewer(df_rows)
    rows = df_rows.to_dict("records")
    median_single = calculate_median(rows)
    all_rows = load_all_data(departments)
    df_all_rows = pd.DataFrame(all_rows)
    df_all_rows = remove_NaT_format(df_all_rows)
    all_rows = relative(df_all_rows).to_dict("records")
    median_all = calculate_median(all_rows)
    data["rows"] = rows
    data["median_single"] = median_single
    data["median_all"] = median_all

    return render_template(
        "writer-dashboard.html",
        data=data,
        writer=writer,
        last_exams=last_exams,
        start_date=start_date,
        end_date=end_date,
        version=version,
        departments=departments,
    )


@app.route("/reviewer-dashboard")
def reviewer_dashboard():
    reviewer = request.args.get("r", "")
    last_exams = request.args.get("last_exams", 30)
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    departments = request.args.getlist("departments") or [
        "AOD",
        "CTD",
        "MSK",
        "NUK",
        "IR",
        "FPS",
        "MAM",
        "NR",
        "UKBB",
    ]
    departments = "{" + ",".join(departments) + "}"
    modalities = request.args.getlist("modalities") or [
        "CT",
        "MRI",
        "US",
        "RX",
        "OTHER",
    ]
    modalities = "{" + ",".join(modalities) + "}"
    rows = load_data_by_reviewer(
        reviewer, last_exams, start_date, end_date, departments, modalities
    )
    df_rows = pd.DataFrame(rows)
    df_rows = relative(df_rows)
    df_rows = remove_NaT_format(df_rows)
    data = calculate_median_by_writer(df_rows)
    rows = df_rows.to_dict("records")
    median_single = calculate_median(rows)
    all_rows = load_all_data(departments)
    df_all_rows = pd.DataFrame(all_rows)
    df_all_rows = remove_NaT_format(df_all_rows)
    all_rows = relative(df_all_rows).to_dict("records")
    median_all = calculate_median(all_rows)
    data["rows"] = rows
    data["median_single"] = median_single
    data["median_all"] = median_all
    return render_template(
        "reviewer-dashboard.html",
        data=data,
        reviewer=reviewer,
        last_exams=last_exams,
        start_date=start_date,
        end_date=end_date,
        version=version,
        departments=departments,
    )


def load_data_by_writer(
    writer, last_exams, start_date, end_date, departments, modalities
):
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    if start_date and end_date:
        s_d = datetime.strptime(start_date, "%d.%m.%Y")
        e_d = datetime.strptime(end_date, "%d.%m.%Y")
        rows = query_by_writer_and_date_and_department_and_modality(
            cursor, writer, s_d, e_d, departments, modalities
        )
    else:
        rows = query_by_writer_and_department_and_modality(
            cursor, writer, last_exams, departments, modalities
        )
    return rows


def load_data_by_reviewer(
    reviewer, last_exams, start_date, end_date, departments, modalities
):
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    if start_date and end_date:
        s_d = datetime.strptime(start_date, "%d.%m.%Y")
        e_d = datetime.strptime(end_date, "%d.%m.%Y")
        rows = query_by_reviewer_and_date_and_department_and_modality(
            cursor, reviewer, s_d, e_d, departments, modalities
        )
    else:
        rows = query_by_reviewer_and_department_and_modality(
            cursor, reviewer, last_exams, departments, modalities
        )
    return rows


def load_all_data(departments):
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    return query_all_by_departments(cursor, departments)


def remove_NaT_format(df):
    return df.fillna("None")



def get_review_db():
    "Returns a connection to the PostgreSQL Review DB"
    db = getattr(g, "_review_database", None)
    if db is None:
        db = g._review_database = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return g._review_database


def get_ris_db():
    """ Returns a connection to the Oracle db. """
    db = getattr(g, "_ris_database", None)
    if db is None:
        db = g._ris_database = open_connection(**RIS_DB_SETTINGS)
    return g._ris_database


@app.teardown_appcontext
def teardown_db(exception):
    """ Closes DB connection when app context is done. """
    logging.debug("Closing db connection")
    db = getattr(g, "_ris_database", None)
    if db is not None:
        db.close()
