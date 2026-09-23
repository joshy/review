# RIS/Review Report Server

## RIS Connection
A connection to the RIS database is established and the reports are downloaded
locally. This is GE Centricity specific. Also the view is very specific.

*BEWARE: This is not a general solution*

## System dependencies
 * Oracle driver


## URL
 * load specific report use URL
      `show?accession_number=<accession_number>`
 * load specific report, formatted as text
      `show?accession_number=<accession_number>&output=text`



## Review App
Install PostgreSQL
Run following commands
 * CREATE ROLE repo with LOGIN PASSWORD '******';
 * ALTER ROLE repo CREATEDB;
Login with `repo` user and run the following commands
 * psql postgres -U repo
 * CREATE DATABASE review_app;
 * GRANT ALL PRIVILEGES ON DATABASE review_app TO repo;

## Testing

From the `review` folder, with `.env` present and `TESTING=true` (skips Entra login and who-is-who):

```
uv sync
uv run python -m review.app
```

`TESTING_HOST` and `TESTING_PORT` are read only when `TESTING=true`. They default to `127.0.0.1` and `5000`. `flask run` ignores them and always binds port 5000.

To compare both databases, use two copies of the project (or two `.env` files) and give the second one another port, for example `TESTING_PORT=5001`. Then open http://127.0.0.1:5000/ and http://127.0.0.1:5001/.

You are treated as an admin. With `mssql_db_enabled = false` (the default) the list and dashboards query the old PostgreSQL database (`REVIEW_DB_*`). Set `mssql_db_enabled = true` and fill in `mssql_db_*` to use the new SQL Server instead. The PostgreSQL path stays in place.

The change-tracking job is separate and is not required to open the UI:

```
uv run python track_changes.py
```