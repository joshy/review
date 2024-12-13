import logging
import os
import click
import psycopg2
from sqlalchemy import create_engine, text
from psycopg2.extras import DictCursor
import datetime

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


def secta_cdwh_connection():
    logging.debug("Opening connection to sectra db")
    user = os.getenv("SECTRA_USER")
    password = os.getenv("SECTRA_PASSWORD")
    hostname = os.getenv("SECTRA_HOST")
    port = os.getenv("SECTRA_PORT")
    dbname = os.getenv("SECTRA_DB")
    engine = create_engine(
        f"mssql+pymssql://{user}:{password}@{hostname}:{port}/{dbname}"
    )
    return engine


@click.group()
def cli():
    """CLI Script with Accession Number."""
    pass


@cli.command()
@click.argument("accession_number", type=str)
@click.option(
    "--mode",
    type=click.Choice(["metric", "hedging"]),
    default="hedging",
    help="update either metrics or hedging",
)
@click.option("--bulk", type=click.Choice(['10', '100', '1000', '10000', '100000']), help="How many rows to fetch")
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


@cli.command()
@click.option('--day', type=click.DateTime(formats=["%Y-%m-%d"]), help="Specify a single day (format: YYYY-MM-DD).")
@click.option('--start-date', type=click.DateTime(formats=["%Y-%m-%d"]), help="Start date of the range (format: YYYY-MM-DD).")
@click.option('--end-date', type=click.DateTime(formats=["%Y-%m-%d"]), help="End date of the range (format: YYYY-MM-DD).")
def fix_dates(day, start_date, end_date):
    """
    Fixes dates based on the provided options.
    Provide either a single day or a date range.
    """
    if day and (start_date or end_date):
        click.echo("Error: Provide either --day or --start-date/--end-date, not both.")
        return

    if not (day or start_date):
        click.echo("Error: You must provide either --day or --start-date/--end-date.")
        return

    if start_date and not end_date:
        click.echo("Error: You must provide both --start-date and --end-date for a range.")
        return

    if day:
        click.echo(f"Fixing dates for the single day: {day.strftime('%Y-%m-%d')}")
        # Add your query logic here
        run_query_for_day(day)


    elif start_date and end_date:
        if start_date > end_date:
            click.echo("Error: Start date cannot be after end date.")
            return
        click.echo(f"Fixing dates for the range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        # Add your query logic here
        run_query_for_date_range(start_date, end_date)

def run_query_for_day(day):
    """Mock function to run a query for a single day."""
    click.echo(f"Running query for the day: {day.strftime('%Y-%m-%d')}")
    sql = """
        select
            e.ExaminationAccessionNumber,
            e.ExaminationDate
        from
            Examinations e
        where
            e.ExaminationDate >= :start_date
            and e.ExaminationDate <= :end_date
            and e.ExaminationAccessionNumber LIKE '3%'
        """
    engine = secta_cdwh_connection()
    with engine.connect() as con:
        result = con.execute(text(sql), 
                             {"start_date" : f"{day.strftime('%Y-%m-%d')} 00:00:00",
                              "end_date": f"{day.strftime('%Y-%m-%d')} 23:59:59"})
        results = result.mappings().all()

    print(len(results))
    connection = get_review_db()
    for i in results:
        sql = """
                UPDATE sectra_reports
                SET unters_beginn = %s
                WHERE accession_number = %s
                RETURNING accession_number;
            """
        try:
            cursor = connection.cursor(cursor_factory=DictCursor)
            cursor.execute(sql,(i.ExaminationDate, i.ExaminationAccessionNumber))
            print(i.ExaminationDate, i.ExaminationAccessionNumber)
        except psycopg2.Error as e:
            logging.error("Error %s", e)
    connection.commit()
    cursor.close()

def run_query_for_date_range(start_date, end_date):
    """Mock function to run a query for a date range."""
    click.echo(f"Running query for the range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    current_date = start_date
    while current_date <= end_date:
        run_query_for_day(current_date)
        current_date += datetime.timedelta(days=1)



if __name__ == "__main__":
    cli()
