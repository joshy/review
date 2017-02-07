import logging
import os
from flask import Flask, render_template, g, request

from repo.database import open_connection
from repo.report import get_as_html, get_as_txt

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('repo.default_config')
app.config.from_pyfile('config.cfg')
app.config['VERSION'] = '0.0.3'


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
        return render_template('plain.html', report=report_as_text, meta_data=meta_data)

    else:
        report_as_html, meta_data = get_as_html(con.cursor(), accession_number)
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


if __name__ == "__main__":
    app.run()
