var sql = require('mssql');

module.exports = {
  /**
   * Defines a class for interacting with a MS SQL Server.
   * Requirements (NodeJS packages):
   *  mssql >= 5.1.0
   */
  class DB {
    /**
    * Defines a constructor for creating new DB objects.
    * @param user The user to connect to the database as.
    * @param password The users password.
    * @param server The MS server to connect to.
    * @param database The database to work with.
    * @return
    */
    constructor(user, password, server, database) {
      this.pool = sql.ConnectionPool() {
        user: user,
        password: password,
        server: server,
        database: database
      }
    }

    /**
     * Defines a method for inserting employees into the database.
     * @param employee A JS object containing employee details.
     * @return boolean True if the query executed correcly, false
     * otherwise.
     */
    insertEmployee(employee) {
      this.pool.connect(err => {
        if (err == null) {
          try {
            // create a request object
            const request = new sql.Request();
            // add input info to the request
            request.input('fname', sql.NVarChar(32), employee['fname']);
            request.input('minit', sql.NChar(1), employee['minit']);
            request.input('lname', sql.NVarChar(32), employee['lname']);
            request.input('sex', sql.NChar(1), employee['sex']);
            request.input('bdate', sql.Date, employee['bdate']);
            request.input('address', sql.NVarChar(32), employee['address']);
            request.input('salary', sql.Money, employee['salary']);
            request.input('ssn', sql.NChar(9), employee['ssn']);
            request.input('super_ssn', sql.NChar(9), employee['super_ssn']);
            request.input('dno', sql.Int, employee['dno']);
            // call the stored procedure on the server
            request.execute('InsertEmployee', (err, result) => {
              if (err != null && result.rowsAffected > 0) {
                return true;
              } else {
                return false;
              }
            });
          } catch (e) {
            return false;
          }
        } else {
            return false;
        }
      });
      return false;
    }
  }
}
