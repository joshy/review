import os
from datetime import datetime

import pandas as pd
import psycopg2
import structlog
from flask import Flask, g, redirect, render_template, request, session, url_for
from flask_assets import Bundle, Environment
from flask_session import Session
from httpx import get
from identity.flask import Auth
from psycopg2.extras import RealDictCursor
from striprtf.striprtf import rtf_to_text
from werkzeug.middleware.proxy_fix import ProxyFix

import review.app_config as app_config
from review.calculations import (
    calculate_median,
    calculate_median_by_reviewer,
    calculate_median_by_writer,
    relative,
)
from review.database import (
    query_all_by_departments,
    query_by_reviewer_and_date_and_modality,
    query_by_reviewer_and_modality,
    query_by_writer_and_date_and_modality,
    query_by_writer_and_modality,
    query_review_report_by_acc,
    query_review_reports,
)
from review.hedging import highlight_hedging

log = structlog.get_logger()

REVIEW_DB_SETTINGS = {
    "dbname": os.getenv("REVIEW_DB_NAME"),
    "user": os.getenv("REVIEW_DB_USER"),
    "password": os.getenv("REVIEW_DB_PASSWORD"),
    "host": os.getenv("REVIEW_DB_HOST"),
    "port": os.getenv("REVIEW_DB_PORT"),
}

WHO_IS_WHO_URL = os.getenv("WHO_IS_WHO_URL")

VERSION = "4.1.2"


def create_app():
    app = Flask(__name__)
    app.config.from_object(app_config)

    # Set the secret key to some random bytes. Keep this really secret!
    app.secret_key = b'_5#y2L"F4QA458z\n\xec]/'

    # Initialize extensions
    Session(app)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Add Jinja2 extensions
    app.jinja_env.add_extension("jinja2.ext.loopcontrols")
    app.jinja_env.add_extension("jinja2.ext.do")

    # Initialize auth
    auth = Auth(
        app,
        authority=app_config.AUTHORITY,
        client_id=app_config.CLIENT_ID,
        client_credential=app_config.CLIENT_SECRET,
        redirect_uri="http://localhost:8443/getAToken",
    )

    # Initialize JS assets
    init_js(app)

    # Register routes
    register_routes(app, auth)

    log.info("starting review app")
    return app


def init_js(app):
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


def register_routes(app, auth):
    @app.route(app_config.REDIRECT_PATH)
    def auth_response():
        result = auth.complete_log_in(request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        return redirect(url_for("review"))

    @app.route("/")
    @auth.login_required()
    def review(*, context):
        log.info("review")
        user = context["user"]
        now = datetime.now().strftime("%d.%m.%Y")
        day = request.args.get("day", now)
        if not is_admin(user):
            writer = user["samAccountName"]
        else:
            writer = request.args.get("writer", "")
        reviewer = request.args.get("reviewer", "")
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
            version=VERSION,
            has_general_approval_rights=is_admin,
        )

    @app.route("/no_rights")
    def no_rights():
        return "Sorry, you have no rights to view this page", 401

    @app.route("/diff/<id>")
    @auth.login_required()
    def diff(id, *, context):
        con = get_review_db()
        row = query_review_report_by_acc(con.cursor(), id)
        cases = ["report_s", "report_v", "report_f"]
        for c in cases:
            if c in row:
                field = c + "_text"
                v = row[c]
                if v:
                    row[field] = rtf_to_text(v, encoding="iso8859-1", errors="ignore")

        hedging_score_v = "-"
        if "report_v_text" in row:
            row["report_v_text"], hedging_score_v = highlight_hedging(
                row["report_v_text"]
            )

        hedging_score_s = "-"
        if "report_s_text" in row:
            row["report_s_text"], hedging_score_s = highlight_hedging(
                row["report_s_text"]
            )

        row["report_f_text"], hedging_score_f = highlight_hedging(row["report_f_text"])

        return render_template(
            "diff.html",
            hedging_score_s=hedging_score_s,
            hedging_score_v=hedging_score_v,
            hedging_score_f=hedging_score_f,
            row=row,
            version=VERSION,
        )

    @app.route("/writer-dashboard")
    @auth.login_required()
    def writer_dashboard(*, context):
        user = context["user"]
        if not is_admin(user):
            writer = user["samAccountName"]
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
            version=VERSION,
            has_general_approval_rights=is_admin,
        )

    @app.route("/reviewer-dashboard")
    @auth.login_required()
    def reviewer_dashboard(*, context):
        user = context["user"]
        if not is_admin(user):
            return redirect(url_for("no_rights"))
        reviewer = request.args.get("r", "")
        if reviewer == "":
            reviewer = user["samAccountName"]
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
        rows = load_data_by_reviewer(
            reviewer, last_exams, start_date, end_date, modalities
        )
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
            version=VERSION,
            has_general_approval_rights=is_admin,
        )


def is_admin(user):
    if "is_admin" in session:
        return session["is_admin"]
    log.debug("is_admin not set in session, checking via who_is_who")
    loginname = user.get("samAccountName")
    who_is_who_user = get(WHO_IS_WHO_URL + loginname).json()
    session["user"] = user | who_is_who_user
    admin_users = os.getenv("ADMIN_USERS")
    session["is_admin"] = False
    if (
        loginname in admin_users
        or session["user"]["ris"]["has_general_approval_rights"]
    ):
        session["is_admin"] = True
    return session["is_admin"]


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
