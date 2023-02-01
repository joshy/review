import logging
import os
from datetime import datetime

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, request, url_for
from flask_assets import Bundle, Environment
from flask_login import LoginManager, current_user
from flask_login.utils import login_required
from psycopg2.extras import RealDictCursor
from striprtf.striprtf import rtf_to_text

from requests import get

from review.calculations import (
    calculate_median,
    calculate_median_by_reviewer,
    calculate_median_by_writer,
    relative,
)
from review.database import (
    query_review_reports,
    query_review_report_by_acc,
    query_all_by_departments,
    query_by_reviewer_and_date_and_modality,
    query_by_reviewer_and_modality,
    query_by_writer_and_date_and_modality,
    query_by_writer_and_modality,
)
from review.user import User

app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.jinja_env.add_extension("jinja2.ext.do")
version = app.config["VERSION"] = "4.1.2"

login_manager = LoginManager()
login_manager.init_app(app)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4QA458z\n\xec]/'

load_dotenv()


REVIEW_DB_SETTINGS = {
    "dbname": os.getenv("REVIEW_DB_NAME"),
    "user": os.getenv("REVIEW_DB_USER"),
    "password": os.getenv("REVIEW_DB_PASSWORD"),
    "host": os.getenv("REVIEW_DB_HOST"),
    "port": os.getenv("REVIEW_DB_PORT"),
}

WHO_IS_WHO_URL = os.getenv("WHO_IS_WHO_URL")

"""
if not WHO_IS_WHO_URL:
    logging.error("WHO_IS_WHO_URL is not set, quitting!")
    sys.exit(1)
"""

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


@login_manager.request_loader
def load_user_from_request(request):
    loginname = request.headers.get("Remote-User")
    if loginname:
        user = get(WHO_IS_WHO_URL + loginname).json()
        user = User(user)
        # If the RIS username is not empty return user, otherwise user
        # doesn't exists. Check whoiswho application for implementation details
        if not user.login_name:
            return None
        return user
    elif "localhost" in request.headers.get("Host"):
        d = {"ris": {"mitarb_kuerzel": "CYRJO", "has_general_approval_rights": True}}
        return User(d)
    # finally, return None if both methods did not login the user
    return None


@app.route("/")
@login_required
def review():
    now = datetime.now().strftime("%d.%m.%Y")
    day = request.args.get("day", now)
    if not current_user.has_general_approval_rights():
        writer = current_user.login_name()
    else:
        writer = request.args.get("writer", "")
        if writer != "" and "@" not in writer:
            writer = writer + "@ms.uhbs.ch"
    reviewer = request.args.get("reviewer", "")
    if reviewer != "" and "@" not in reviewer:
            reviewer = reviewer + "@ms.uhbs.ch"
    report_status = request.args.get("report_status", "")
    dd = datetime.strptime(day, "%d.%m.%Y")
    con = get_review_db()
    rows = query_review_reports(con.cursor(), dd, writer, reviewer, report_status)
    day = dd.strftime("%d.%m.%Y")
    return render_template(
        "review.html",
        rows=rows,
        day=day,
        writer=writer,
        reviewer=reviewer,
        version=version,
        has_general_approval_rights=current_user.has_general_approval_rights(),
    )


@app.route("/no_rights")
def no_rights():
    return "Sorry, you have no rights to view this page", 401


@app.route("/diff/<id>")
def diff(id):
    con = get_review_db()
    row = query_review_report_by_acc(con.cursor(), id)
    cases = ["report_s", "report_v", "report_f"]
    for c in cases:
        if c in row:
            field = c + "_text"
            v = row[c]
            if v:
                row[field] = rtf_to_text(v, encoding="iso8859-1", errors="ignore")
    return render_template("diff.html", row=row, version=version)


@app.route("/writer-dashboard")
@login_required
def writer_dashboard():
    if not current_user.has_general_approval_rights():
        writer = current_user.login_name()
    else:
        writer = request.args.get("w", "")
    last_exams = request.args.get("last_exams", default=30, type=int)
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    modalities = request.args.getlist("modalities") or [
        "CT",
        "MRI",
        "US",
        "RX",
        "OTHER",
    ]
    modalities = "{" + ",".join(modalities) + "}"
    rows = load_data_by_writer(writer, last_exams, start_date, end_date, modalities)
    df_rows = pd.DataFrame(rows)
    df_rows = relative(df_rows)
    df_rows = remove_NaT_format(df_rows)
    data = calculate_median_by_reviewer(df_rows)
    rows = df_rows.to_dict("records")
    median_single = calculate_median(rows)
    all_rows = load_all_data()
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
        has_general_approval_rights=current_user.has_general_approval_rights(),
    )


@app.route("/reviewer-dashboard")
@login_required
def reviewer_dashboard():
    if not current_user.has_general_approval_rights():
        return redirect(url_for("no_rights"))
    reviewer = request.args.get("r", "")
    last_exams = request.args.get("last_exams", default=30, type=int)
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    modalities = request.args.getlist("modalities") or [
        "CT",
        "MRI",
        "US",
        "RX",
        "OTHER",
    ]
    modalities = "{" + ",".join(modalities) + "}"
    rows = load_data_by_reviewer(reviewer, last_exams, start_date, end_date, modalities)
    df_rows = pd.DataFrame(rows)
    df_rows = relative(df_rows)
    df_rows = remove_NaT_format(df_rows)
    data = calculate_median_by_writer(df_rows)
    rows = df_rows.to_dict("records")
    median_single = calculate_median(rows)
    all_rows = load_all_data()
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
        has_general_approval_rights=current_user.has_general_approval_rights(),
    )


def load_data_by_writer(writer, last_exams, start_date, end_date, modalities):
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    if start_date and end_date:
        s_d = datetime.strptime(start_date, "%d.%m.%Y")
        e_d = datetime.strptime(end_date, "%d.%m.%Y")
        rows = query_by_writer_and_date_and_modality(
            cursor, writer, s_d, e_d, modalities
        )
    else:
        rows = query_by_writer_and_modality(cursor, writer, last_exams, modalities)
    return rows


def load_data_by_reviewer(reviewer, last_exams, start_date, end_date, modalities):
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    if start_date and end_date:
        s_d = datetime.strptime(start_date, "%d.%m.%Y")
        e_d = datetime.strptime(end_date, "%d.%m.%Y")
        rows = query_by_reviewer_and_date_and_modality(
            cursor, reviewer, s_d, e_d, modalities
        )
    else:
        rows = query_by_reviewer_and_modality(cursor, reviewer, last_exams, modalities)
    return rows


def load_all_data():
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    return query_all_by_departments(cursor)


def remove_NaT_format(df):
    return df.fillna("None")


def get_review_db():
    "Returns a connection to the PostgreSQL Review DB"
    db = getattr(g, "_review_database", None)
    if db is None:
        db = g._review_database = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return g._review_database
