import logging
import pandas as pd
from datetime import datetime

'''
Opens '../../public/data/changelog.md'
and adds a new entry to the top of the file of the format:
  ###### <3-letter month> <day>, <year>

  - <description of change>

The description of the change is based on './temp/new_papers_abstract.csv'.

The dataframe in that file is grouped by "Conference" and counted.
'''

filtered_conferences = {'CHI'}

def update_changelog(new_papers_filename):
  # Read the new_papers_abstract.csv file
  df = pd.read_csv(new_papers_filename)

  # Group the dataframe by "Conference" and count the number of entries
  grouped_df = df.groupby('Conference').size().reset_index(name='Count')

  # Get the current date in the desired format
  current_date = datetime.now().strftime("%b %d, %Y")

  # Open the changelog.md file in append mode
  with open('../../public/data/changelog.md', 'a') as file:
    # Write the new entry to the top of the file
    # Read the existing content of the changelog.md file
    with open('../../public/data/changelog.md', 'r') as f:
        content = f.read()

    # Create the new entry
    new_entry = f'###### {current_date}\n\n'
    for index, row in grouped_df.iterrows():
        if row["Conference"] in filtered_conferences:
          verb = 'check'
        else:
           verb = 'add'
        new_entry += f'- {verb} {row["Count"]} papers from {row["Conference"]}'
        # add the range of years for the conference
        year_start = df[df["Conference"] == row["Conference"]]["Year"].min()
        year_end = df[df["Conference"] == row["Conference"]]["Year"].max()
        if year_start == year_end:
            new_entry += f'[{year_start}]\n'
        else:
          new_entry += f'[{year_start}–{year_end}]\n'
    new_entry += '\n'

    # Write the new entry followed by the existing content to the file
    with open('../../public/data/changelog.md', 'w') as f:
        f.write(new_entry + content)


if __name__ == '__main__':
    update_changelog('./temp/new_papers_award_abstract.csv')
