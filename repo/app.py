import logging
import os
from datetime import datetime, timedelta

import psycopg2
import schedule
import numpy as np
import pandas as pd
from flask import Flask, g, jsonify, render_template, request, make_response
from flask_assets import Bundle, Environment
from psycopg2.extras import RealDictCursor

from review.database import query_by_writer, query_by_writer_and_date, query_calculations
from review.calculations import relative, calculate_median

from repo.converter import rtf_to_text
from repo.database.connection import open_connection
from repo.database.contrast_medium import query_contrast_medium
from repo.database.report import query_report_by_befund_status
from repo.database.review_report import (query_review_report,
                                         query_review_reports)
from repo.report import get_as_txt, get_as_rtf, get_with_file, q

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('repo.default_config')
app.config.from_pyfile('config.cfg')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
version = app.config['VERSION'] = '3.0.4'

RIS_DB_SETTINGS = {
    'host': app.config['RIS_DB_HOST'],
    'port': app.config['RIS_DB_PORT'],
    'service': app.config['RIS_DB_SERVICE'],
    'user': app.config['RIS_DB_USER'],
    'password': app.config['RIS_DB_PASSWORD']
}

REVIEW_DB_SETTINGS = {
    'dbname': app.config['REVIEW_DB_NAME'],
    'user': app.config['REVIEW_DB_USER'],
    'password': app.config['REVIEW_DB_PASSWORD'],
    'host': 'localhost',
    'port': app.config['REVIEW_DB_PORT']
}

REPORTS_FOLDER = 'reports'
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

assets = Environment(app)
js = Bundle("js/jquery-3.1.0.min.js", "js/moment.min.js",
            "js/pikaday.js", "js/pikaday.jquery.js",
            "js/script.js",
            filters='jsmin', output='gen/packed.js')
assets.register('js_all', js)


@app.route('/')
def main():
    return render_template('index.html', version=app.config['VERSION'])


@app.route('/q')
def query():
    day = request.args.get('day', '')
    dd = datetime.strptime(day, '%Y-%m-%d')
    parse_text = request.args.get('parse', False)
    if not day:
        logging.debug('No day given, returning to main view')
        return main()
    con = get_ris_db()
    rows = q(con.cursor(), dd, parse_text)
    return jsonify(rows)


@app.route('/review')
def review():
    now = datetime.now().strftime('%d.%m.%Y')
    day = request.args.get('day', now)
    writer = request.args.get('writer', '')
    dd = datetime.strptime(day, '%d.%m.%Y')
    con = get_review_db()
    rows = query_review_reports(con.cursor(), dd, writer)
    day = dd.strftime('%d.%m.%Y')
    return render_template('review.html',
        rows=rows, day=day, writer=writer, version=version)


@app.route('/review/diff/<id>')
def diff(id):
    con = get_review_db()
    row = query_review_report(con.cursor(), id)
    cases = ['befund_s', 'befund_g', 'befund_f']
    for c in cases:
        if c in row:
            field = c + '_text'
            v = row[c]
            if v:
                row[field] = rtf_to_text(v)
    return render_template('diff.html', row=row, version=version)


@app.route('/review/dashboard')
def dashboard():
    writer = request.args.get('w', '')
    last_exams = request.args.get('last_exams', 30)
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    rows = load_data(writer, last_exams, start_date, end_date)
    similarity_s_f_single = [x['jaccard_s_f'] for x in rows]
    median_s_f_single = calculate_median(similarity_s_f_single)
    calculations = load_all_data()
    similarity_s_f_all = [x['jaccard_s_f'] for x in calculations]
    median_s_f_all = calculate_median(similarity_s_f_all)
    return render_template('dashboard.html',
        rows=rows, writer=writer, last_exams=last_exams,
        start_date=start_date, end_date=end_date, version=version,
        median_s_f_single=median_s_f_single, median_s_f_all=median_s_f_all)


@app.route('/review/dashboard/data')
def data():
    writer = request.args.get('w', '')
    last_exams = request.args.get('last_exams', 30)
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    rows = load_data(writer, last_exams, start_date, end_date)
    logging.debug(rows)
    if len(rows) > 0:
        df = pd.DataFrame(rows)
        df = relative(df).sort_values('unters_beginn')
        return df.to_csv(index_label='index')
    return pd.DataFrame().to_csv(index_label='index')


def load_data(writer, last_exams, start_date, end_date):
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    if start_date and end_date:
        s_d = datetime.strptime(start_date, '%d.%m.%Y')
        e_d = datetime.strptime(end_date, '%d.%m.%Y')
        rows = query_by_writer_and_date(cursor, writer, s_d, e_d)
    else:
        rows = query_by_writer(cursor, writer, last_exams)
    return rows

def load_all_data():
    con = get_review_db()
    cursor = con.cursor(cursor_factory=RealDictCursor)
    return query_calculations(cursor)

@app.route('/cm')
def cm():
    "Queries for contrast medium for a accession number"
    accession_number = request.args.get('accession_number', '')
    if not accession_number:
        print('No accession number found in request, use accession_number=XXX')
        return main()
    con = get_ris_db()
    result = query_contrast_medium(con.cursor(), accession_number)
    return jsonify(result)


@app.route('/show')
def show():
    """ Renders RIS Report as HTML. """
    accession_number = request.args.get('accession_number', '')
    output = request.args.get('output', 'html')
    # if no accession number is given -> render main page
    if not accession_number:
        print('No accession number found in request, use accession_number=XXX')
        return main()

    con = get_ris_db()
    if output == 'text':
        report_as_text, meta_data = get_as_txt(con.cursor(), accession_number)
        if report_as_text:
            return report_as_text
        else:
            # don't throw an error, no report found -> return empty response
            # because not all accession numbers have a valid report
            return ""
    else:
        report_as_html, meta_data = get_with_file(con.cursor(), accession_number)
        return render_template('report.html',
                               version=app.config['VERSION'],
                               accession_number=accession_number,
                               meta_data=meta_data,
                               report=report_as_html)


@app.route('/download')
def download():
    """ Downloads the original RTF report. """
    accession_number = request.args.get('accession_number', '')
    if not accession_number:
        return ""
    con = get_ris_db()
    report = get_as_rtf(con.cursor(), accession_number)
    response = make_response(report)
    cd = 'attachment; filename={}.rtf'.format(accession_number)
    response.headers['Content-Disposition'] = cd
    return response


def get_review_db():
    "Returns a connection to the PostgreSQL Review DB"
    db = getattr(g, '_review_database', None)
    if db is None:
        db = g._review_database = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return g._review_database


def get_ris_db():
    """ Returns a connection to the Oracle db. """
    db = getattr(g, '_ris_database', None)
    if db is None:
        db = g._ris_database = open_connection(**RIS_DB_SETTINGS)
    return g._ris_database


@app.teardown_appcontext
def teardown_db(exception):
    """ Closes DB connection when app context is done. """
    logging.debug('Closing db connection')
    db = getattr(g, '_ris_database', None)
    if db is not None:
        db.close()
