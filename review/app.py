import logging
import os
from datetime import datetime
from time import perf_counter

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


def configure_logging():
    """Configure application logging from the LOG_LEVEL environment variable."""
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, None)
    invalid_log_level_name = None
    if not isinstance(log_level, int):
        invalid_log_level_name = log_level_name
        log_level_name = "INFO"
        log_level = logging.INFO

    logging.basicConfig(level=log_level, format="%(message)s")
    logging.getLogger().setLevel(log_level)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    if invalid_log_level_name:
        log.warning(
            "invalid log level configured; falling back to INFO",
            configured_log_level=invalid_log_level_name,
        )
    log.info("configured logging", log_level=log_level_name)


def register_logging_hooks(app):
    @app.before_request
    def start_request_logging():
        g._request_started_at = perf_counter()
        g.request_id = request.headers.get("X-Request-ID") or request.headers.get(
            "X-Correlation-ID"
        )

    @app.after_request
    def log_request(response):
        duration_ms = None
        started_at = getattr(g, "_request_started_at", None)
        if started_at is not None:
            duration_ms = round((perf_counter() - started_at) * 1000, 2)

        if getattr(g, "request_id", None):
            response.headers["X-Request-ID"] = g.request_id

        log_method = log.warning if response.status_code >= 500 else log.info
        log_method(
            "request completed",
            method=request.method,
            path=request.path,
            endpoint=request.endpoint,
            status_code=response.status_code,
            duration_ms=duration_ms,
            remote_addr=request.headers.get("X-Forwarded-For", request.remote_addr),
            request_id=getattr(g, "request_id", None),
        )
        return response

    @app.teardown_request
    def log_unhandled_exception(error):
        if error is not None:
            log.exception(
                "request failed",
                method=request.method,
                path=request.path,
                endpoint=request.endpoint,
                error_type=type(error).__name__,
                request_id=getattr(g, "request_id", None),
            )


REVIEW_DB_SETTINGS = {
    "dbname": os.getenv("REVIEW_DB_NAME"),
    "user": os.getenv("REVIEW_DB_USER"),
    "password": os.getenv("REVIEW_DB_PASSWORD"),
    "host": os.getenv("REVIEW_DB_HOST"),
    "port": os.getenv("REVIEW_DB_PORT"),
}

WHO_IS_WHO_URL = os.getenv("WHO_IS_WHO_URL")
# Internal host uses a self-signed certificate; allow disabling verification via .env.
WHO_IS_WHO_VERIFY_SSL = os.getenv("WHO_IS_WHO_VERIFY_SSL", "true").lower() != "false"

VERSION = "4.2.0"


def create_app():
    configure_logging()

    app = Flask(__name__)
    app.config.from_object(app_config)
    register_logging_hooks(app)

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
        redirect_uri=app_config.REDIRECT_URI,
    )

    # Initialize JS assets
    init_js(app)

    # Register routes
    register_routes(app, auth)

    log.info("starting review app", version=VERSION)
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
        log.debug(
            "loaded review reports",
            report_count=len(rows),
            day=dd.strftime("%Y-%m-%d"),
            writer_filter_set=bool(writer),
            reviewer_filter_set=bool(reviewer),
            report_status_filter_set=bool(report_status),
            user_is_admin=is_admin(user),
        )
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
        log.debug("loading report diff")
        con = get_review_db()
        row = query_review_report_by_acc(con.cursor(), id)
        log.debug(
            "loaded report diff source data",
            has_report_s=bool(row.get("report_s")),
            has_report_v=bool(row.get("report_v")),
            has_report_f=bool(row.get("report_f")),
        )
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

        log.debug(
            "calculated report diff hedging scores",
            has_score_s=hedging_score_s != "-",
            has_score_v=hedging_score_v != "-",
            has_score_f=hedging_score_f != "-",
        )

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
        log.debug(
            "prepared writer dashboard data",
            row_count=len(rows),
            all_row_count=len(all_rows),
            writer_filter_set=bool(writer),
            last_exams=last_exams,
            start_date_set=bool(start_date),
            end_date_set=bool(end_date),
            modalities=modalities,
        )
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
        log.debug(
            "prepared reviewer dashboard data",
            row_count=len(rows),
            all_row_count=len(all_rows),
            reviewer_filter_set=bool(reviewer),
            last_exams=last_exams,
            start_date_set=bool(start_date),
            end_date_set=bool(end_date),
            modalities=modalities,
        )
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
        log.debug("using cached admin status", is_admin=session["is_admin"])
        return session["is_admin"]
    log.debug("is_admin not set in session, checking via who_is_who")
    loginname = user.get("samAccountName")
    who_is_who_user = get(WHO_IS_WHO_URL + loginname, verify=WHO_IS_WHO_VERIFY_SSL).json()
    session["user"] = user | who_is_who_user
    admin_users = os.getenv("ADMIN_USERS")
    session["is_admin"] = False
    if (
        loginname in admin_users
        or session["user"]["ris"]["has_general_approval_rights"]
    ):
        session["is_admin"] = True
    log.debug("resolved admin status", is_admin=session["is_admin"])
    return session["is_admin"]


def load_data_by_writer(writer, last_exams, start_date, end_date, modalities):
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    started_at = perf_counter()
    if start_date and end_date:
        s_d = datetime.strptime(start_date, "%d.%m.%Y")
        e_d = datetime.strptime(end_date, "%d.%m.%Y")
        rows = query_by_writer_and_date_and_modality(
            cursor, writer, s_d, e_d, modalities
        )
    else:
        rows = query_by_writer_and_modality(cursor, writer, last_exams, modalities)
    log.debug(
        "loaded writer dashboard rows",
        row_count=len(rows),
        duration_ms=round((perf_counter() - started_at) * 1000, 2),
        date_range_set=bool(start_date and end_date),
        writer_filter_set=bool(writer),
    )
    return rows


def load_data_by_reviewer(reviewer, last_exams, start_date, end_date, modalities):
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    started_at = perf_counter()
    if start_date and end_date:
        s_d = datetime.strptime(start_date, "%d.%m.%Y")
        e_d = datetime.strptime(end_date, "%d.%m.%Y")
        rows = query_by_reviewer_and_date_and_modality(
            cursor, reviewer, s_d, e_d, modalities
        )
    else:
        rows = query_by_reviewer_and_modality(cursor, reviewer, last_exams, modalities)
    log.debug(
        "loaded reviewer dashboard rows",
        row_count=len(rows),
        duration_ms=round((perf_counter() - started_at) * 1000, 2),
        date_range_set=bool(start_date and end_date),
        reviewer_filter_set=bool(reviewer),
    )
    return rows


def load_all_data():
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    started_at = perf_counter()
    rows = query_all_by_departments(cursor)
    log.debug(
        "loaded all department rows",
        row_count=len(rows),
        duration_ms=round((perf_counter() - started_at) * 1000, 2),
    )
    return rows


def remove_NaT_format(df):
    return df.fillna("None")


def get_review_db():
    "Returns a connection to the PostgreSQL Review DB"
    db = getattr(g, "_review_database", None)
    if db is None:
        log.debug("opening review database connection")
        db = g._review_database = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return g._review_database
