import click
import psycopg2
from psycopg2.extras import DictCursor
from review.compare import diffs, hedgings
from review.database import query_review_report_by_acc, update_metrics, update_hedging

from review.app import REVIEW_DB_SETTINGS


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
def main(accession_number, mode):
    """CLI Script with Accession Number."""
    if mode == "metric":
        calculate_metrics(accession_number)
    elif mode == "hedging":
        calculate_hedging(accession_number)


def calculate_hedging(accession_number):
    print(f"Running method calculate_metrics with accession number: {accession_number}")
    db = get_review_db()
    cursor = db.cursor(cursor_factory=DictCursor)
    report = query_review_report_by_acc(cursor, accession_number)
    h = hedgings(report)
    update_hedging(cursor, accession_number, h)


def calculate_metrics(accession_number):
    print(f"Running method calculate_metrics with accession number: {accession_number}")
    db = get_review_db()
    cursor = db.cursor(cursor_factory=DictCursor)
    report = query_review_report_by_acc(cursor, accession_number)
    d = diffs(report)
    update_metrics(cursor, accession_number, d)


if __name__ == "__main__":
    main()
