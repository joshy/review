list:
    @just --list

dev:
    uv run flask --app "review.app:create_app()" run --debug --host 0.0.0.0 --port 8443

poll:
    uv run python runpolling.py

cli *ARGS:
    uv run python cli.py {{ARGS}}

test:
    uv run pytest -v

test-all: test
