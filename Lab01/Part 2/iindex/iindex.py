import csv, pymssql, os, snowballstemmer, sys, string, traceback, re

# used to remove non alphanumeric characters in tokens
nascii_regex = re.compile('[\W_]+', re.UNICODE)
# the translation for remove punctuation
remv_punc = str.maketrans('', '', string.punctuation)
# create the stemming engine
stemmer = snowballstemmer.stemmer('english')

# load in all stop words
stop = set()
try:
    stopfile = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input',
        'stop.txt'
    )
    with open(stopfile) as f:
        for line in f:
            stop.add(line)
except OSError as e:
    print('There was an error reading the stop file! Make sure it exists in the input directory!')
    sys.exit(-1)
except Exception as e:
    print('The following error occurred processing the stop file:')
    print(e)
    print('Cannot continue...')
    sys.exit(-1)

def process_token(token):
    # get the stemmer and punctuation translator
    global stemmer, remv_punc, stop, nascii_regex
    # remove any non alphanumeric characters
    token = nascii_regex.sub('', token)
    # lowercase the token
    token = token.lower()
    # skip stop words and no words
    if token in stop or token is None or token == '':
        return None
    # stem the word
    token = stemmer.stemWord(token)
    return token

def create_index(database, table, host='127.0.0.1', port='1434'):
    """Creates the inverted index on a table in the specified database.

    Arguments:
        database (str): The database holding the state of the union addresses.
        table (str): The name of the table holding the state of the union
        addresses.
        host (str): The hostname of the SQL Server to connect to.
        port (str): The port number of the SQL Server to connect to.
    """

    # table names
    _term_list = 'TermList_Table'

    # try to connect to the database
    try:
        with pymssql.connect(host=host, database=database, port=port, autocommit=True) as conn:
            with conn.cursor(as_dict=True) as read_cursor:
                #
                # PHASE 1: Build the term and doc number table
                #
                print('\nCreating document frequency table...')
                read_cursor.execute(
                """
                DROP TABLE IF EXISTS TermList_Table
                CREATE TABLE TermList_Table (
                    Term NVARCHAR(32) NOT NULL,
                    Term_Freq INT NOT NULL,
                    Doc_Year NVARCHAR(4) NOT NULL
                )
                """
                )
                print('==> Retrieving speeches from {}.{}...'.format(database, table))
                # get the state of the union addresses, parse them one at a time
                read_cursor.execute('SELECT * FROM {}'.format(table))
                # create the table for the term doc#
                tokens = list()
                for row in read_cursor.fetchall():
                    print('===> Processing address given on {} by {}...'.format(
                        row['DateGiven'], row['Speaker']
                    ))

                    # get the year
                    try:
                        year = row['DateGiven'].split('-')[2]
                    except:
                        year = row['DateGiven']

                    # remove any punctuation
                    for proc_tk in map(process_token, row['Speech'].split(' ')):
                        if not proc_tk:
                            continue
                        # add the word to the documents term list
                        tokens.append((proc_tk, 1, year))
                    read_cursor.executemany(
                        "INSERT INTO TermList_Table VALUES (%s, %d, %s)",
                        tokens
                    )
                    tokens.clear()
                print('\nCreating sorted term list table...')
                read_cursor.execute(
                """
                DROP PROCEDURE IF EXISTS SP_CreateSortedTermTable
                """
                )
                # create the sorted table procedure -- creates if it doesn't
                #   exist, otherwise modifes it for this pipeline
                # requires SQL server 2016+
                read_cursor.execute(
                """
                CREATE PROCEDURE SP_CreateSortedTermTable
                AS
                DROP TABLE IF EXISTS Sorted_Table
                CREATE TABLE Sorted_Table (
                    Term NVARCHAR(32) NOT NULL,
                    Term_Freq INT NOT NULL,
                    Doc_Year NVARCHAR(4) NOT NULL
                )
                INSERT INTO Sorted_Table
                    SELECT * FROM TermList_Table
                    ORDER BY Doc_Year, Term
                """
                )
                print('\nCreating term lookup table...')
                # calls the above procedure to create the sorted term table
                read_cursor.callproc('SP_CreateSortedTermTable')
                # create a procedure for generating the termlookuptable
                read_cursor.execute(
                """
                DROP PROCEDURE IF EXISTS SP_CreateTermLookupTable
                """
                )
                read_cursor.execute(
                """
                CREATE PROCEDURE SP_CreateTermLookupTable
                AS
                DROP TABLE IF EXISTS TermLookUpTable
                CREATE TABLE TermLookUpTable (
                    Term VARCHAR(32) NOT NULL,
                    Doc_Year VARCHAR(4) NOT NULL,
                    Term_Freq INT NOT NULL
                )
                INSERT INTO TermLookUpTable
                    SELECT Term, Doc_Year, SUM(Term_Freq)
                    FROM Sorted_Table
                    GROUP BY Doc_Year, Term
                    ORDER BY Doc_Year, Term
                """
                )
                # calls the above procedure to create the termlookuptable
                read_cursor.callproc('SP_CreateTermLookupTable')


    except Exception as e:
        print('\nThe following error occurred processing the inverted index:')
        traceback.print_exc()
        print('\nCannot continue...')
