import logging
import daiquiri

daiquiri.setup(level=logging.DEBUG,
    outputs=(
        daiquiri.output.File('repo-errors.log', level=logging.ERROR),
        daiquiri.output.RotatingFile(
            'repo-debug.log',
            level=logging.DEBUG,
            # 10 MB
            max_size_bytes=10000000)
    ))

from repo.app import app

app.run(host='0.0.0.0', port=7777)
