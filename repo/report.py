import glob
import logging
from typing import Optional

from repo.converter import html, text, jjson
from repo.writer import write
from repo.database import load_report


def get_as_html(cursor, accession_number):
    # cursor, string -> Optional[str]
    report, meta_data = _load_write(cursor, accession_number)
    return html(report), jjson(meta_data)


def get_as_txt(cursor, accession_number):
    # cursor, string -> Optional[str]
    report, meta_data = _load_write(cursor, accession_number)
    return text(report), jjson(meta_data)


def _load_write(cursor, accession_number):
    # cursor, string -> Optional[str]
    report_file_ref, meta_data_file_ref = _lookup(accession_number)
    if report_file_ref is None:
        report_file_ref, meta_data_file_ref = load_report(cursor, accession_number)
        report_file_ref = write(accession_number, report_file_ref, meta_data_file_ref)
    return report_file_ref, meta_data_file_ref


def _lookup(accession_number):
    # cursor, string -> Tuple[Optional[str], Optional[str]]
    logging.info('Looking accession number %s locally', accession_number)
    rtf = glob.glob('reports/*' + accession_number + '.rtf')
    meta_data = glob.glob('reports/*' + accession_number + '.json')
    if len(rtf) > 0 and len(meta_data) > 0:
        logging.info('Found accession number %s and meta data %s locally',
                     accession_number, meta_data)
        return rtf[0], meta_data[0]
    else:
        return None, None
