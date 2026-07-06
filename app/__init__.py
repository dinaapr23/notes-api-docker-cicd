from flask import Flask
from app import db


def create_app(test_config=None):
    """Application factory.

    DB_PATH is read from the environment so the same code runs against a
    persistent SQLite file (mounted on a Docker volume) in Docker Compose,
    and against an in-memory SQLite database during automated testing
    (no external database service needed for CI).
    """
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    db.init_db()

    from app.routes import bp as notes_bp
    app.register_blueprint(notes_bp)

    return app
