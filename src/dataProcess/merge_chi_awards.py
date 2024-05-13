import json
import pandas as pd

'''
This checks the CHI Program files to find papers that won awards, and updates the corresponding dataset.

The program files `CHI_20XX_program.json` contains various data. The relevant array is the "contents" attributes.
This is a list of paper objects. Each paper object has various attributes, two are relevant. "title" and "award",

The `chi.csv` file contains the current list of chi papers as a csv. This CSV contains a `Title`, and `Award` column.

This script should read all event program files, between CHI_2018_program.json to CHI_2023_program.json and update the corresponding row
in the chi.csv file. "HONORABLE_MENTION" should map to "HM", and "BEST_PAPER" should map to "BP".
'''

# Function to update the chi.csv file
def update_chi_csv(program_file, csv_file):
    # Load the program file
    with open(program_file, 'r') as f:
        program_data = json.load(f)

    # Load the chi.csv file into a pandas DataFrame
    csv_data = pd.read_csv(csv_file)

    # Update the chi.csv file based on the program data
    for paper in program_data['contents']:
        title = paper['title']
        
        # If there is no award attribute, then skip paper
        if 'award' not in paper:
            continue

        award = paper['award']

        # Map the award to the corresponding value
        if award == 'HONORABLE_MENTION':
            award = 'HM'
        elif award == 'BEST_PAPER':
            award = 'BP'

        # Update the corresponding row in the chi.csv file
        csv_data.loc[csv_data['Title'] == title, 'Award'] = award

    # Write the updated data back to the chi.csv file
    csv_data.to_csv(csv_file, index=False)

# Call the update_chi_csv function for each program file
for year in range(2018, 2024):
    program_file = f'./temp/CHI/CHI_{year}_program.json'
    csv_file = 'chi.csv'
    update_chi_csv(program_file, csv_file)
