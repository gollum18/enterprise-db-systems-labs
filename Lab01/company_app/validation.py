# Name: validation.py
# Since: 9/18/2019
# Author: Christen Ford
# Purpose: Validates form data entered on the home page.

import regex

from collections.abc import Mapping
from numbers import Number


# defines a few simple regular expressions for validating input format
regex_ssn = r'^([1-9])([0-9]{2})([1-9])([0-9])([1-9])([0-9]{3})'gm
regex_dno = r'^([0-9]+)$'gm
# unused since the database stores the salary as an integer not decimal
regex_salary = r'^([0-9]+)(\.)([0-9]{2})$'gm


def _validate_range(value, min, max=None):
    """Validates a range for a number or string.

    In the case of a number, min and max are taken to be the numeric lower
    and upper bounds on value | min <= value <= max.

    In the case of a string, min and max are taken to be the numeric lower
    and upper bounds on the strings length | min <= len(value) <= max.

    Arguments:
        value (numbers.Number|str): A number or string.
        min (int): The minimum legal range for the specified value.
        max (int): The maximum legal value for the specified value
        (default: None). If not specified then it is assumed there is no
        upper bound on value.

    Returns:
        (boolean): True if the value is in the specified range, False
        otherwise or if the value is not supported.
    """
    if isinstance(value, Number):
        if max:
            return value >= lower
        return lower <= value <= max
    elif isinstance(value, str):
        if max:
            return len(value) >= max
        return lower <= len(value) <= max
    else:
        return False


def validate(msg):
    """Validates form data passed via the home page.

    Msg is a Python type implementing collections.abc.Mapping. Msg should
    contain the following key/value pairs:
    -- fname/str
    -- minit/str
    -- lname/str
    -- address/str
    -- bdate/str
    -- salary/number
    -- sex/str
    -- ssn/str
    -- super_ssn/str
    -- dno/number

    Arguments:
        msg (collections.abc.Mapping): A mapping type.
    """
    # validate the first name
    if 'fname' in msg:
        if not instanceof(msg['fname'], str):
            return {"result": False, 'reason': ''}
        if not _validate_range(msg['fname'], 1, 32):
            return {"result": False, 'reason': ''}
    else:
        return {"result": False, 'reason': ''}
    # validate the middle initial
    if 'minit' in msg:
        if not instanceof(msg['minit'], str):
            return {"result": False, 'reason': ''}
        if not _validate_range(msg['minit'], 0, 1):
            return {"result": False, 'reason': ''}
    else:
        return {"result": False, 'reason': ''}
    # validate the last name
    if 'lname' in msg:
        if not instanceof(msg['lname'], str):
            return {"result": False, 'reason': ''}
        if not _validate_range(msg['lname'], 1, 32):
            return {"result": False, 'reason': ''}
    else:
        return {"result": False, 'reason': ''}
    # validate the address
    if 'address' in msg:
        if not instanceof(msg['address'], str):
            return {"result": False, 'reason': ''}
        if not _validate_range(msg['address'], 3, 32):
            return {"result": False, 'reason': ''}
    else:
        return {"result": False, 'reason': ''}
    # validate the birthday
    if 'bdate' in msg:
        if not instanceof(msg['bdate'], str):
            return {"result": False, 'reason': ''}
        # TODO: Validate the date is an actual, valid date
    else:
        return {"result": False, 'reason': ''}
    # validate the salary
    if 'salary' in msg:
        if not instanceof(msg['salary'], Number):
            return {"result": False, 'reason': ''}
        if not _validate_range(msg['salary'], 1):
            return {"result": False, 'reason': ''}
    else:
        return {"result": False, 'reason': ''}
    # validate the sex
    if 'sex' in msg:
        if not instanceof(msg['sex'], str):
            return {"result": False, 'reason': ''}
        if msg['sex'] != 'M' and msg['sex'] != 'F':
            return {"result": False, 'reason': ''}
    else:
        return {"result": False, 'reason': ''}
    # validate the ssn
    if 'ssn' in msg:
        if not instanceof(msg['ssn'], str):
            return {"result": False, 'reason': ''}
        if not regex.match(regex_ssn, msg['ssn']):
            return {"result": False, 'reason': ''}
    else:
        return {"result": False, 'reason': ''}
    # validate the supervisor ssn
    if 'super_ssn' in msg:
        if not instanceof(msg['super_ssn'], str):
            return {"result": False, 'reason': ''}
        if not regex.match(regex_ssn, msg['super_ssn']):
            return {"result": False, 'reason': ''}
    else:
        return {"result": False, 'reason': ''}
    # validate the department number
    if 'dno' in msg:
        if not instanceof(msg['dno'], Number):
            return {"result": False, 'reason': ''}
    else:
        return {"result": False, 'reason': ''}

    # everything checked out return true
    return {"result": True, 'reason': ''}
