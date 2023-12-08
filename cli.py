import logging

import click
import psycopg2
from psycopg2.extras import DictCursor

from review.app import REVIEW_DB_SETTINGS
from review.compare import diffs, hedgings
from review.database import query_review_report_by_acc, update_hedging, update_metrics, query_report_for_hedging


# Set the logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_review_db():
    db = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return db


@click.command()
@click.argument("accession_number", type=str)
@click.option(
    "--mode",
    type=click.Choice(["metric", "hedging"]),
    default="hedging",
    help="update either metrics or hedging",
)
@click.option("--bulk", type=click.Choice(['10', '100', '1000', '10000']), help="How many rows to fetch")
def main(accession_number, mode, bulk):
    """CLI Script with Accession Number."""
    if mode == "metric":
        calculate_metrics(accession_number)
    elif mode == "hedging":
        calculate_hedging(accession_number, bulk)


def calculate_hedging(accession_number, bulk=None):
    logging.info(f"Running calculate_hedging with accession number: {accession_number}")
    connection = get_review_db()
    cursor = connection.cursor(cursor_factory=DictCursor)
    if bulk is None:
        report = query_review_report_by_acc(cursor, accession_number)
        h = hedgings(report)
        update_hedging(cursor, accession_number, h)
        connection.commit()
        cursor.close()
    else:
        rows = query_report_for_hedging(cursor, bulk)
        for row in rows:
            h = hedgings(row)
            update_hedging(cursor, row["accession_number"], h)
        connection.commit()
        cursor.close()


def calculate_metrics(accession_number):
    logging.info(f"Running calculate_metrics with accession number: {accession_number}")
    connection = get_review_db()
    cursor = connection.cursor(cursor_factory=DictCursor)
    report = query_review_report_by_acc(cursor, accession_number)
    d = diffs(report)
    update_metrics(cursor, accession_number, d)
    connection.commit()
    cursor.close()


if __name__ == "__main__":
    main()
