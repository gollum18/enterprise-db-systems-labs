# Name: qaparser.py
# Since: 09/29/2019
# Author: Christen Ford
# Purpose: Implements simple parsing of SQL-like queries.
#   The following three operations are supported:
#       SELECTION,
#       PROJECTION,
#       JOIN (NESTED LOOPS)
# The operations in this module are defined to function with queries in the
#   following form:
#       Selection InTable_Name Selection_Conditions OutTab_Name1
#       Nested Loop Join LTable RTable Join_Conditions OutTab_Name2
#       Projection InTable_Name2 ProjectColumn_List OutTab_Name3
# Note that this module interacts with a SQL Server database to pull down the
#   initial dataset for the parser.

import click, pymssql
import csv, sys, os


def is_int(string):
    """Determines if a string is an integer.

    Arguments:
        string (str): The string to check.

    Returns:
        (boolean): True if the string is an integer, False otherwise.
    """
    try:
        int(string)
    except ValueError:
        return False
    return True


def get_condition(cond_token, split_tokens):
    """Generates a condition from a condition token.

    Arguments:
        cond_token (str): A condition token of the form:
            key|op|value (ignoring |)
        split_tokens (list): A list of strings tokens to split on.

    Returns:
        (set): A tuple containing the following format:
            key: The field pertaining to the condition.
            op: The conditions operator.
            value: The value to compare against the field.
    """
    import re
    pattern = r"({kwds})".format(kwds=split_tokens)
    cond_parts = re.split(pattern, cond_token)
    key = cond_parts[0]
    op = cond_parts[1]
    value = int(cond_parts[2]) if is_int(cond_parts[2]) else cond_parts[2]
    return (key, op, value)


class QAEngine(object):
    """Defines an engine for parsing QA queries. CUrrently the QAEngine supports
    selection, projection, and join operations via the following tokens:
        Selection: Selection
        Projection: Projection
        Join: Join
    By default the QAEngine is case-insensitive. You can disable this feature either
    during object creation or after an instance of the QAEngine has been instantiated.
    """

    def __init__(self, host='127.0.0.1', port=1433, database='COMPANY', case_sensitive=False):
        """Returns a new instance of a QAEngine instance configured to point
        at the specified database.

        Arguments:
            host (str): The IPV4 address of the backing SQL Server.
            port (int): The port number of the backing SQL Server.
            database (str): The database to perform the queries against.
            case_sensitive (boolean): Whether QA queries are treated as case-sensitive
            or not.
        """
        self._host = host
        self._port = port
        self._database = database
        self._case_sensitve = case_sensitive
        self._tables = dict()


    def selection(self, in_table, out_table, conditions):
        """Implements SQL-like selection operation to filter rows from a relation.
        rows in in_table that do not meet all of the conditions specified are
        filtered out and not preserved to out_table.

        Arguments:
            in_table (list): A list of rows from a relation.
            out_table (list): A list of rows from a relation.
            conditions (list): A list of rows of the following form:
                    (key, op, value)
                Where...
                    key is the column to filter on
                    op is one of {=, !=, <, <=, >, >=}
                    value is the value to filter against

        Returns:
            (generator): A generator over the result set.
        """
        # empty the out table if it exists already
        if out_table in self._tables:
            self._tables[out_table].clear()
        else:
            self._tables[out_table] = []
        # read in the table from memory
        for row in self.read_table(in_table):
            # used to determine whether to keep the row or not
            add_row = True
            for condition in conditions:
                key = condition[0]
                op = condition[1]
                value = condition[2]
                if op == '=' and not row[key] == value:
                    add_row = False
                    break
                elif op == '!=' and not row[key] != value:
                    add_row = False
                    break
                elif op == '<' and not row[key] < value:
                    add_row = False
                    break
                elif op == '>' and not row[key] > value:
                    add_row = False
                    break
                elif op == '>=' and not row[key] >= value:
                    add_row = False
                    break
            # add the row to the out table
            if add_row:
                self._tables[out_table].append(dict(row))
        # write out the out table
        self.write_table(out_table)


    def projection(self, in_table, out_table, project_list):
        """Implements SQL-like selection operation to project fields from a relation.

        Arguments:
            in_table (str): The name of the input table for the projection.
            out_table (str): The name of the table to write the projection
            results to.
            project_list (list): The list of fields to project.

        Returns:
            (generator): A generator over the result set.
        """
        # empty the out table if it exists already
        if out_table in self._tables:
            self._tables[out_table].clear()
        else:
            self._tables[out_table] = []
        # build the output table in memory
        for row in self.read_table(in_table):
            self._tables[out_table].append(
                {key:value for key, value in row.items() if key in project_list}
            )
        # write the output table to disk
        self.write_table(out_table)


    def join(self, left_table, right_table, out_table, conditions):
        """Implements SQL-like join operation to join rows from two relations based
        on specified conditions.

        Arguments:
            left_table (str): The left table to join on.
            right_table (str): The right table to join against.
            out_table (str): The table to write the join results to.
            conditions (list): A list containing rows of the following form:
                    (left_key, op, right_key)
                Where...
                    left_key is the key from the left table
                    op is one of: {=}
                    right_key is the key from right table

        Returns:
            (generator): A generator over the result set.
        """
        # empty the out table if it exists already
        if out_table in self._tables:
            self._tables[out_table].clear()
        else:
            self._tables[out_table] = []
        # join the records from the two tables together based on conditions
        #   specified - p and q are dict object
        for p in self.read_table(left_table):
            for q in self.read_table(right_table):
                # make sure that the conditions match
                add_row = True
                # make sure that all of the conditions check out before join
                for condition in conditions:
                    left_key = condition[0]
                    op = condition[1]
                    right_key = condition[2]
                    if op == '=' and not p[left_key] == q[right_key]:
                        add_row = False
                        break
                # join the relations together
                if add_row:
                    self._tables[out_table].append(dict(p, **q))
        # write the contents of the table to disk
        self.write_table(out_table)


    def run(self, query_steps):
        """Parses the query steps in query_steps in sequential order
        using the operations defined by this class.

        Arguments:
            query_steps (list): A Python list containing the steps for the
            SQL-like query.

        Returns:
            (list): A list of rows containing the table
        """
        split_tokens = '|'.join(['=', '!=', '<', '<=', '>', '>='])
        for step in query_steps:
            # lowercase the query step
            step = step.lower()
            # split the step along space
            parts = step.split(' ')
            # get the operation, and out table
            op = parts[0]
            out_table = parts[-1]
            # handle the op appropriately
            if op == 'selection':
                in_table = parts[1]
                conditions = [
                    get_condition(cond, split_tokens) for cond in parts[2:-1]
                ]
                self.selection(in_table, out_table, conditions)
            elif op == 'join':
                left_table = parts[1]
                right_table = parts[2]
                conditions = [
                    get_condition(cond, split_tokens) for cond in parts[3:-1]
                ]
                self.join(left_table, right_table, out_table, conditions)
            elif op =='projection':
                in_table = parts[1]
                project_list = [part.replace(',', '') for part in parts[2:-1]]
                self.projection(in_table, out_table, project_list)
            else:
                click.echo('\'{}\' operation is unsupported!'.format(step))
                break
        # empty out the tables from memory
        self._tables.clear()


    def write_table(self, table_name):
        """Writes the contents of a table from memory to disk.

        Arguments:
            table_name (str): The name of the table to write to disk.
        """
        filename = '{}.tsv'.format(table_name)
        try:
            with open(filename, 'w', newline='') as tsvfile:
                writer = csv.writer(tsvfile, delimiter='\t', quotechar='|',
                    quoting=csv.QUOTE_MINIMAL)
                # write out the header row for the table
                writer.writerow(self._tables[table_name][0].keys())
                # write out the data rows for the table
                for row in self._tables[table_name]:
                    writer.writerow(row.values())
        except Exception:
            click.secho('ERROR: There was a problem writing tsv file: {}'.format(filename), fg='red')
            # delete the tsv file if there was an issue creating it
            if os.path.exists(filename):
                os.remove(filename)
        except Exception:
            click.secho('ERROR: A general error has occurred. Now aborting...', fg='red')
            sys.exit(-1)


    def read_table(self, table_name):
        """Reads the contents of a table from memory or SQL Server if not
        in memory.

        Tables read from SQL Server are NOT stored in memory.

        Arguments:
            table_name (str): The name of the table to read.

        Returns:
            (generator): A Python generator that yields QArows over the contents
            of a table pointed to by table_name.
        """
        # check if we need to read the table from SQL Server
        if table_name not in self._tables:
            try:
                # connect to the server
                with pymssql.connect(host=self._host,
                                     port=self._port,
                                     database=self._database) as conn:
                    # create a cursor to get stuff from the server
                    with conn.cursor(as_dict=True) as cursor:
                        # get the records from the server
                        cursor.execute(
                            """
                            SELECT * FROM {}
                            """.format(table_name)
                        )
                        for row in cursor:
                            yield {k.lower(): v for k, v in row.items()}
            except Exception:
                click.secho('ERROR: Could not connect to the SQL Server instance. Now aborting...', fg='red')
                sys.exit(-1)
        else:
            for row in self._tables[table_name]:
                yield row


@click.command()
@click.argument('infile', default='input.qa', type=click.Path(exists=True))
@click.option('-h', '--host', default='127.0.0.1', help='IPV4 address of SQL Server data source.')
@click.option('-p', '--port', default=1433, help='TCP port number of the SQL Server data source.')
@click.option('-d', '--database', default='COMPANY', help='The database to perform reads against.')
def main(infile, host, port, database):
    """Runs the QAEngine on the specified QA file to produce intermediate tables
    from a SQL Server source. Output files are written out as {TableName}_out.tsv.

    Arguments:
        infile (str): The filepath to the QA file (default: 'input.qa').
        host (str): The host address of the SQL Server instance (default: '127.0.0.1').
        port (int): The port number of the SQL Server instance (default: 1433).
        database (str): The database to run the QA query against (default: COMPANY).
    """
    # get the query steps from file
    try:
        with open(infile) as f:
            query_steps = list()
            for line in f:
                line = line.replace('\n', '')
                query_steps.append(line)
    except IOError:
        click.echo('IOError: Indicated qa file not found!')
        sys.exit(-1)
    # create the QA engine
    qae = QAEngine(host, port, database)
    # pass the query off to the qae engine
    qae.run(query_steps)


if __name__ == '__main__':
    main()
