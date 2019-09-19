# To run this program on Windows:
# Note that the first three steps only need done once
#   virtualenv venv
#   ./Scripts/activate
#   python setup.py install
#   set FLASK_APP=company-app (cmd) | $env:FLASK_APP = "company-app" (ps)
#   set FLASK_ENV=development (cmd) | $env:FLASK_ENV = "development" (ps)
#   flask run

# To run this program on Linux/Max:
# Note that the first three steps only need done once
#   virtualenv venv
#   ./Scripts/activate
#   python setup.py install
#   export FLASK_APP=company-app
#   export FLASK_ENV=development
#   flask run

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
