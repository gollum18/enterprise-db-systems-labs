import pymssql

from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """Gets a connection to the database.

    Returns:
        (pymssql.Connection): A connection to the database.
    """
    if 'db' not in g:
        # TODO: Hook these up
        g.db = pymssql.connect(
            # you shouldnt have to change anything here unless SQL server
            #   is not running on the default port
            # this uses windows auth by default -- make sure the current logged
            #   in user has proper access rights to the database
            host='127.0.0.1',
            port='1434',
            database='COMPANY',
            # specify a user and password below if needed
            #user=''
            #password=''
        )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
