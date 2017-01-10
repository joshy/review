import glob
import logging

from repo.converter import html, text
from repo.writer import write
from repo.database import load_report


def get_as_html(cursor, accession_number):
    report = _lookup(accession_number)
    if report is None:
        report = load_report(cursor, accession_number)
        report = write(accession_number, report)
    return html(report)


def get_as_txt(cursor, accession_number):
    report = _lookup(accession_number)
    if report is None:
        report = load_report(cursor, accession_number)
        report = write(accession_number, report)

    return text(report)


def _lookup(accession_number):
    logging.info('Looking accession number %s locally', accession_number)
    results = glob.glob('reports/*' + accession_number + '.rtf')
    if len(results) > 0:
        logging.info('Found accession number %s locally', accession_number)
        return results[0]
    else:
        return None
