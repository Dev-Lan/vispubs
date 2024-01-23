import csv
import os
'''
This file updates the `resources` column in the PAPER_LIST_FILENAME csv file.
For every row it will find the DOI value, then it will find the corresponding
paper link file in the ROOT_FOLDER. It will then read the contents of the file
to determine which icons are used. It will then update the `resources` column
with the appropriate value. The keys are separated by semicolons.
The possible values are:
    P - paper
    V - video
    C - code
    W - website
    D - data
    O - other
'''

PAPER_LIST_FILENAME = '../../public/data/papers.csv'
ROOT_FOLDER = '../../public/data/paperLinks/'

def update_paper_link_flags():
    with open(PAPER_LIST_FILENAME, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    for row in rows:
        doi = row['DOI']
        resource_file = os.path.join(ROOT_FOLDER, doi)

        if os.path.exists(resource_file):
            with open(resource_file, 'r') as file:
                contents = file.readlines()
            icons = set([x.split(',')[-1].strip() for x in contents])

            flags = []
            if 'project_website' in icons:
                flags.append('PW')
            if 'paper' in icons:
                flags.append('P')
            if 'video' in icons:
                flags.append('V')
            if 'code' in icons:
                flags.append('C')
            if 'data' in icons:
                flags.append('D')
            if 'other' in icons:
                flags.append('O')
            
            row['Resources'] = ';'.join(flags)

    with open(PAPER_LIST_FILENAME, 'w', newline='') as csvfile:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == '__main__':
    update_paper_link_flags()
