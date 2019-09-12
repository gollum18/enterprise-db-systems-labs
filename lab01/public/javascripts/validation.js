// first and last name must be two or more consecutive characters
const regex_name = '/^[a-zA-Z]{2,}/g';
// only one character for middle initial and it should be uppercase
const regex_minit = '/^[A-Z]{1}/g';
// ssn must be 9 consecutive digits: 1st, 4th, 6th digits > 0, others 0 - 9
const regex_ssn = '/^([1-9])([0-9]{2})([1-9])([0-9])([1-9])([0-9]{3})$/g';

/**
 * Attempts to convert the date string to a Date object.
 * @param value A Datestring to convert to a date.
 * @return An object containing the following keys:
 *  result: True if the datestring is correct, false otherwise.
 *  date: The Date object. null if result is false.
 */
Date.tryParse(date) {
  try {
    let temp = new Date(date);
    if (date.toString() === 'Invalid Date') {
      return {result: false, value: null};
    }
    return {result: true, value: temp};
  } catch (err) {
    return {result: false, value: null};
  }
}

/**
 * Attempts to convert a string to a float.
 * @param float The float string to parse.
 * @return An object containing the following keys:
 *  result: True if the float was parsed correctly, false otherwise.
 *  value: The float string as a float.
 */
Number.tryParseFloat(float) {
  try {
    let value = parseFloat(salary);
    return {result: true, value: value};
  } catch (err) {
    return {result: false, value: null};
  }
}

/**
 * Redefinition of lodash has client-side.
 * @param object The object to check against.
 * @param property The property to check for.
 * @return True if the object has the indicated property, false otherwise.
 */
function has(object, property) {
  return object ? hasOwnProperty.call(object, key) : false;
}

/**
 * Validates an employees name.
 * @param first The employees first name.
 * @param minit [optional] The initial of the employees middle name.
 * @param last The employees last name.
 * @return True if the employee name is ok, false otherwise.
 */
function validateEmployeeName(first, minit, last) {
  // check the first and last names
  if (name === null || last === null) {
    return {result: false, reason: 'First or last name not provided!'};
  }
  if (typeof name !== 'string' || typeof last != 'string') {
    return {result: false, reason: 'First or last name not a valid type!'};
  }
  if (!first.match(regex_name) || !last.match(regex_name)) {
    return {result: false,
      reason: 'First or last name must be at least two characters long!'};
  }
  // check the middle initial if there is one
  if (minit != null) {
    if (typeof minit !== 'string') {
      return {result: false, reason: 'Middle initial not a valid type!'};
    }
    if (!minit.matches(regex_minit)) {
      return {result: false,
      reason: 'Middle initial must be exactly one uppercase character!'};
    }
  }
  return {result: true, reason: ''};
}

/**
 * Validates an employees SSN.
 * @param ssn The employees Social Security number.
 * @return True if the employees SSN is ok, false otherwise.
 */
function validateEmployeeSSN(ssn) {
  if (ssn === null) {
    return {result: false, reason: 'SSN not provided'};
  }
  if (typeof ssn !== "string") {
    return {result: false, reason: 'SSN not a valid type!'};
  }
  if (!ssn.match(regex_ssn)) {
    return {result: false, reason: 'SSN must be nine consecutive digits!'};
  }
  return {result: true, reason: ''};
}

/**
 * Validates an employees birthday.
 * @param bdate The employees birthday.
 * @return True if the employees birthday is ok, false otherwise.
 */
function validateEmployeeBirthday(bdate) {
  if (date === null) {
    return {result: false, reason: 'Birthday not provided!'};
  }
  if (typeof bdate != "string") {
    return {result: false, reason: 'Birthday not a valid type!'};
  }
  let date = Date.tryParse(bdate);
  if (!date.result) {
    return {result: false, reason: 'Birtyday not understood!'};
  }
  return {result: true, reason: ''};
}

/**
 * Validates an employees address.
 * @param address The employees address.
 * @return True if the employees address is ok, false otherwise.
 */
function validateEmployeeAddress(address) {
  if (address === null) {
    return {result: false, reason: 'Address not provided!'};
  }
  if (typeof address !== 'string') {
    return {result: false, reason: 'Address not a valid type!'};
  }
  if (address.length() < 8) {
    return {result: false,
      reason: 'Address must be at least eight characters long!'};
  }
  return {result: true, reason: ''};
}

/**\
 * Validates an employees sex.
 * @param sex The employees sex.
 * @return True if the employees sex is ok, false otherwise.
 */
function validateEmployeeSex(sex) {
  if (sex === null) {
    return {result: false, reason: 'Sex not provided!'};
  }
  if (typeof sex !== 'string') {
    return {result: false, reason: 'Sex not a valid type!'};
  }
  if (sex !== 'M' || sex !== 'F') {
    return {result: false, reason: 'Sex must be M or F!'};
  }
  return {result: true, reason: ''};
}

/**
 * Validates an employees salary.
 * @param salary The employees salary.
 * @return True if the employees salary is ok, false otherwise.
 */
function validateEmployeeSalary(salary) {
  let tp = Number.tryParseFloat(salary);
  if (tp.result) {
    if (tp.value <= 0) {
      return {result: false, reason: ''};
    } else {
      return {result: false, reason: ''};
    }
  } else {
    return {result: false, reason: ''};
  }
  return {result: true, reason: ''};
}

/**
 * Validates employee info before submitting it to the server.
 * @param employee The employee object to validate.
 * @return True if the employee validates correctly, false otherwise.
 */
function validateInfo(employee) {
  let vResult;

  // verify the employee name
  if (has(employee, 'fname') &&
      has(employee, 'lname')) {
    if (has(employee, 'minit')) {
      vResult = validateEmployeeName(employee['fname'],
                                     employee['minit'],
                                     employee['lname'])
      if (!vResult.result) {
        return vResult;
      }
    } else {
      vResult = validateEmployeeName(employee['fname'],
                                     null,
                                     employee['lname'])
      if (!vResult.result) {
        return vResult;
      }
    }
  } else {
    return {result: false, reason: 'No employee name information provided!'};
  }

  // validate the employees ssn
  if (has(employee, 'ssn')) {
    vResult = validateEmployeeSSN(employee.ssn);
    if (!vResult.result) {
      return vResult;
    }
  } else {
    return {result: false, reason: ''};
  }

  // validate the employees birthday
  if (has(employee, 'bdate')) {
    vResult = validateEmployeeBirthday(employee.bdate);
    if (!vResult.result) {
      return vResult;
    }
  } else {
    return {result: false, reason: ''};
  }

  // validate the employeees address
  if (has(employee, 'address')) {
    vResult = validateEmployeeAddress(employee.address);
    if (!vResult.result) {
      return vResult;
    }
  } else {
    return {result: false, reason: ''};
  }

  // validate the employees sex
  if (has(employee, 'sex')) {
    vResult = validateEmployeeSex(employee.sex);
    if (!vResult.result) {
      return vResult;
    }
  } else {
    return {result: false, reason: ''};
  }

  // validate the employees salary
  if (has(employee, 'salary')) {
    vResult = validateEmployeeSalary(employee.salary)
    if (!vResult.result) {
      return vResult;
    }
  } else {
    return {result: false, reason: ''};
  }

  // verify super ssn
  if (has(employee, 'super_ssn')) {
    vResult = validateEmployeeSSN(employee.super_ssn);
      if (!vResult.result) {
        return vResult;
      }
  } else {
    return {result: false, reason: ''};
  }

  return {result: true, reason: ''};
}
