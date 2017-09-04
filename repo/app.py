import logging
import os
import schedule
import psycopg2
from datetime import datetime, timedelta

from flask import Flask, g, jsonify, render_template, request
from flask_assets import Bundle, Environment

from repo.database.connection import open_connection
from repo.database.contrast_medium import query_contrast_medium
from repo.database.report import query_report_by_befund_status
from repo.database.review_report import query_review_reports
from repo.report import get_as_txt, q

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('repo.default_config')
app.config.from_pyfile('config.cfg')
app.config['VERSION'] = '1.1.0'

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
    'password': app.config['REVIEW_DB_PASSWORD']
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
    if not day:
        logging.debug('No day given, returning to main view')
        return main()
    con = get_ris_db()
    rows = q(con.cursor(), dd)
    return jsonify(rows)


@app.route('/review')
def review():
    con =  get_review_db()
    now = datetime.now()
    rows = query_review_reports(con.cursor(), now)
    return render_template('review.html', rows=rows)


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
    print(accession_number)
    # if no accession number is given -> render main page
    if not accession_number:
        print('No accession number found in request, use accession_number=XXX')
        return main()

    con = get_ris_db()
    if output == 'text':
        print('using text')
        report_as_text, meta_data = get_as_txt(con.cursor(), accession_number)
        return report_as_text
    else:
        report_as_html, meta_data = get_as_txt(con.cursor(), accession_number)
        print(report_as_html)
        return render_template('report.html',
                               version=app.config['VERSION'],
                               accession_number=accession_number,
                               meta_data=meta_data,
                               report=report_as_html)


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
