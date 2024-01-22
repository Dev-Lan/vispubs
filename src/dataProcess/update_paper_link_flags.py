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