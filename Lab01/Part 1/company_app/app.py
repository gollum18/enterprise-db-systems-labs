import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        ENV='development',
        DEBUG=True,
        SECRET_KEY='dev'
    )

    if test_config is None:
        # Load the instance config, if it exists when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instence filder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database
    from . import db
    db.init_app(app)

    # register the views with the application
    from . import index
    app.register_blueprint(index.bp)

    return app
