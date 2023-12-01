import click
import psycopg2
from psycopg2.extras import DictCursor
from review.compare import diffs
from review.database import query_review_report_by_acc, update_metrics

from review.app import REVIEW_DB_SETTINGS

def get_review_db():
    db = psycopg2.connect(**REVIEW_DB_SETTINGS)
    return db


@click.command()
@click.argument("accession_number", type=str)
def main(accession_number):
    """CLI Script with Accession Number."""
    calculate_metrics(accession_number)

def calculate_metrics(accession_number):
    # Replace this with the actual implementation of your method
    print(f"Running method calculate_metrics with accession number: {accession_number}")
    db = get_review_db()
    cursor = db.cursor(cursor_factory=DictCursor)
    report = query_review_report_by_acc(cursor, accession_number)
    d = diffs(report)
    update_metrics(cursor, accession_number, d)


if __name__ == "__main__":
    main()