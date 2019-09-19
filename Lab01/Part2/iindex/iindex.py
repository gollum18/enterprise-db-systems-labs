import click, csv, os, sys
from . import db


@click.command('create')
@click.option('-f', '--filename', 
              default='./input/UnionAddressTable.csv')
def create_index(filename, output):
    # create the output directory if it does not exist
    os.mkdir('output')
    # pipeline the processing for the output file
    
        
        
# invoke the primary command
if __name__ == '__main__':
    create_index()
