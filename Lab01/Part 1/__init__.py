from . import app
import os

def main():
    # setup the flask environment variables
    os.putenv("FLASK_APP", "company-app")
    os.putenv("FLASK_ENV", "development")
    # start the flask app
    app.create_app().run()

if __name__ == '__main__':
    main()
