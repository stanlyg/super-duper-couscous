#!/bin/python3

from pathlib import Path
import argparse
import csv
import sys

parser = argparse.ArgumentParser(description='Builds MySQL tables based on CSV files. This program takes a naive approach, and considers all fields as text type fields. The CREATE TABLE code will create CHAR (for 8 or fewer characters), VARCHAR (between 9 and 255 characters), or TEXT (for more than 255 characters) field types.', epilog="If you prefer, you can pipe the output of this program drirectly to mysql, and it will probably work, if you specify the database on at least one of them.")
parser.add_argument("infile", help="Input CSV file")
parser.add_argument("-v","--verbose", help="Display verbose output (Processed {n} lines).", action="store_true")
parser.add_argument("-d","--database", help="Database name to use as a prefix for the tables.",default="")
parser.add_argument("-t","--table", help="Table name to use instead of the base file name.",default="")
parser.add_argument("--drop", help="Add DROP table IF EXISTS to output.",action="store_true",default=False)
parser.add_argument("--no-create", help="Prevents the CREATE statement from being created",action="store_true",default=False)
parser.add_argument("--no-load", help="Prevents the LOAD statement from being created",action="store_true",default=False)
args = parser.parse_args()

pipedoutput = not sys.stdout.isatty()

sourcefile = Path(args.infile)
if not sourcefile.exists() or not sourcefile.is_file():
    print(f"The source file, {sourcefile}, does not exist or is not a file.")
    exit(2)

if len(args.table) > 0:
    table_name=args.table
else:
    table_name=sourcefile.stem

if len(args.database) > 0:
    db_prefix=args.database+'.'
else:
    db_prefix=''

if args.no_create and args.no_load:
    if pipedoutput:
        print('-- ',end='')
    print("With both the --no-create and --no-load options, there's nothing left to do. Goodbye.")
    exit(3)

with sourcefile.open(mode='r') as csv_file:

    csv_reader = csv.DictReader(csv_file)
    fields = csv_reader.fieldnames

    fieldsizes = {}
    for field in fields:
        fieldsizes[field] = 0

    row = next(csv_reader)

    line_count = 0

    for row in csv_reader:
        for field in fields:
            if len(row[field]) > fieldsizes[field]:
                fieldsizes[field] = len(row[field])
        line_count += 1
    if args.verbose:
        if pipedoutput:
            print(f'select \'Processed {line_count} lines\' as \'\';')
        else:
            print(f'Processed {line_count} lines.')

    if args.drop:
        print(f'DROP TABLE IF EXISTS {db_prefix}{table_name};')

    if args.no_create is False:
        print('\n\nCREATE TABLE ',end="")
        print(f'{db_prefix}{table_name} ( ',end="")
        print(f'{table_name}_id INT NOT NULL AUTO_INCREMENT, ',end="")
        for field in fields:
            if fieldsizes[field] < 8:
                print(f'{field} CHAR ({fieldsizes[field]}), ',end='')
            elif fieldsizes[field] < 256:
                print(f'{field} VARCHAR ({fieldsizes[field]}), ',end="")
            else:
                print(f'{field} TEXT, ',end="")
        print(f'PRIMARY KEY ({table_name}_id) ',end="")
        print(');\n\n')

    if args.no_load is False:
        print(f'LOAD DATA LOCAL INFILE \'{sourcefile}\' INTO TABLE {db_prefix}{table_name} ',end="")
        print('FIELDS TERMINATED BY \',\' ENCLOSED BY \'"\' LINES TERMINATED BY \'\\r\\n\' IGNORE 1 LINES (',end="")
        print(", ".join(fields),end="")
        print(');')

