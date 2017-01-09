from flask import Flask, render_template, g, request

from repo.database import load_report, open_connection
from repo.writer import write


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('repo.default_config')
app.config.from_pyfile('config.cfg')
app.config['VERSION'] = '0.0.1'


DB_SETTINGS = {
    'host': app.config['DB_HOST'],
    'port': app.config['DB_PORT'],
    'service': app.config['DB_SERVICE'],
    'user': app.config['DB_USER'],
    'password': app.config['DB_PASSWORD']
}

@app.route('/')
def main():
    return render_template('index.html', version=app.config['VERSION'])

@app.route('/show')
def show():
    """ Renders RIS Report as HTML. """
    accession_number = request.args.get('accession_number', '')
    con = get_db()
    report_as_html = load_report(con.cursor(), accession_number)
    return render_template('report.html',
                           version=app.config['VERSION'],
                           accession_number=accession_number,
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
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run()
