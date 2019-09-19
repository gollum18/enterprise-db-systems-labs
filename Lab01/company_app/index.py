import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import get_db

bp = Blueprint('index', __name__, url_prefix='/')

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # get user data from the form
        fname = request.form['fname']
        minit = request.form['minit']
        lname = request.form['lname']
        ssn = request.form['ssn']
        bdate = request.form['bdate']
        address = request.form['address']
        sex = request.form['sex']
        salary = request.form['salary']
        super_ssn = request.form['super_ssn']
        dno = request.form['dno']

        # prime an error message if needed
        error = None

        # validate the information passed from the form
        from . import validation

        msg = dict()
        msg['fname'] = fname
        msg['minit'] = minit
        msg['lname'] = lname
        msg['ssn'] = ssn
        msg['bdate'] = bdate
        msg['address'] = address
        msg['sex'] = sex
        msg['salary'] = salary
        msg['super_ssn'] = super_ssn
        msg['dno'] = dno
        resp = validation.validate(validation_msg)
        if resp['result']:
            # get the database
            db = get_db()

            try:
                # insert the employee using the stored procedure in the db
                with db.cursor(as_dict=True) as cursor:
                    cursor.callproc(
                        # this is the stored procedure name
                        'SP_Insert_NewEmployee',
                        # these are the arguments for the stored procedure
                        (
                            fname, minit, lname, ssn, bdate,
                            address, sex, salary, super_ssn, dno
                        )
                    )
                flash('Record successfully inserted into database!')
            except Exception:
                flash('There was an error connecting to the database!')
        else:
            flash(resp['reason'])

    return render_template('index/index.html')


@bp.route('/projects', methods=['GET'])
def projects():
    db = get_db()
    context = dict()

    try:
        # as_dict=True will allow us to access the columns in each row by name
        #   ex: row['fname'] will yield the contents of the 'fname' column
        # get the mployee records
        with db.cursor(as_dict=True) as cursor:
            cursor.execute("SELECT * FROM EMPLOYEES")
            context['employees'] = [row for row in cursor.fetchall()]

        # get the project records
        with db.cursor(as_dict=True) as cursor:
            cursor.execute("SELECT * FROM WORKS_ON")
            context['projects'] = [row for row in cursor.fetchall()]
    except Exception:
        flash('Redirected to Home: There was an error connection to the database!')
        return redirect(url_for('index.index'))

    return render_template('index/projects.html', **context)
