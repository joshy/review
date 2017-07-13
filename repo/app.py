import logging
import os

from datetime import datetime
from flask import Flask, render_template, g, request, jsonify

from repo.database import open_connection
from repo.report import get_as_txt, query_report

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('repo.default_config')
app.config.from_pyfile('config.cfg')
app.config['VERSION'] = '0.0.5'


DB_SETTINGS = {
    'host': app.config['DB_HOST'],
    'port': app.config['DB_PORT'],
    'service': app.config['DB_SERVICE'],
    'user': app.config['DB_USER'],
    'password': app.config['DB_PASSWORD']
}

REPORTS_FOLDER = 'reports'
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER, exist_ok=True)


@app.route('/')
def main():
    return render_template('index.html', version=app.config['VERSION'])


@app.route('/q')
def query():
    day = request.args.get('day', '')
    dd = datetime.strptime(day, '%Y-%m-%d')
    if not day:
        print('No day given, returning main')
        return main()
    con = get_db()
    rows = query_report(con.cursor(), dd)
    return jsonify(rows)


@app.route('/show')
def show():
    """ Renders RIS Report as HTML. """
    accession_number = request.args.get('accession_number', '')
    output = request.args.get('output', 'html')

    # if no accession number is given -> render main page
    if len(accession_number) == 0:
        return main()

    con = get_db()
    if output == 'text':
        report_as_text, meta_data = get_as_txt(con.cursor(), accession_number)
        return report_as_text

    elif output == 'json':
        report_as_text, meta_data = get_as_txt(con.cursor(), accession_number)

    else:
        report_as_html, meta_data = get_as_txt(con.cursor(), accession_number)
        return render_template('report.html',
                               version=app.config['VERSION'],
                               accession_number=accession_number,
                               meta_data=meta_data,
                               report=report_as_html)


def get_db():
    """ Returns a connection to the Oracle db. """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = open_connection(**DB_SETTINGS)
    return g._database


@app.teardown_appcontext
def teardown_db(exception):
    """ Closes DB connection when app context is done. """
    logging.debug('Closing db connection')
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
