from . import iindex

def main():
    print('''This tool will walk you through creating an inverted index over the state of the union addresses for lab 1.''')
    print('''In order for this tool to function, please ensure that the target SQL Server instance has a table defined with the following attributes and is pre-populated with all necessary information:''')
    print(
    '''
        Schema:\n
        \tSpeaker - varchar(50) - not null\n
        \tDate - varchar(30) - not null\n
        \tWeblink - varchar(200)\n
        \tFilelink - varchar(200)\n
        \tAddress - ntext\n
    ''')
    host = input("SQL Server host address ex. 127.0.0.1: ")
    port = input("SQL Server port number ex. 1434: ")
    database = input("The database holding the above table: ")
    table = input("The table adhering to the specifed above schema: ")
    print('-'*80)
    print("""Now attempting to create inverted index on state of the union addresses in {}.{} @ {}:{}, standby...""".format(database, table, host, port))
    iindex.create_index(host=host, port=port, database=database, table=table)

if __name__ == '__main__':
    main()
