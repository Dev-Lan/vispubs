import logging
from calendar import c
import csv
import os
from venv import create
'''
This file creates stub files for every paper specified in `PAPER_LIST_FILENAME` CSV.
It will create the file based on the DOI folder column of the csv. The DOI contains two
parts separated by a slash. The first part is the folder name and the second part is the
file name. If the folder does not exist it will create the folder and the file. If the
folder and file already exist it will not modify the file.

The base contents for the stub file is the following:
name,url,icon
'''

PAPER_LIST_FILENAME = '../../public/data/papers.csv'
ROOT_FOLDER = '../../public/data/paperLinks/'
BASE_CONTENTS = 'name,url,icon'

def create_stub_files():
    logger = logging.getLogger('create_stub_files')
    with open(PAPER_LIST_FILENAME, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        skipped_count = 0
        created_count = 0
        for row in reader:
            doi = row[3]
            doi_folder, doi_file = row[3].rsplit('/', 1)

            folder_path = os.path.join(ROOT_FOLDER, doi_folder)
            file_path = os.path.join(folder_path, doi_file)

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            if not os.path.exists(file_path):
                with open(file_path, 'w') as stub_file:
                    stub_file.write(BASE_CONTENTS)
                    created_count += 1
            else:
                skipped_count += 1
    logger.info(f'Created {created_count} files and skipped {skipped_count} files.')

if __name__ == '__main__':
    create_stub_files()
