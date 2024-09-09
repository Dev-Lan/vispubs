# thanks chatgpt for writing 95% of this.

import pandas as pd
import logging

# Conference,Year,Title,DOI,Abstract,AuthorNames-Deduped,Award

def combine():
  logger = logging.getLogger('combine')
  # Load the CSV files into pandas DataFrames
  folder = './intermediate/'
  df1 = pd.read_csv(folder + 'VIS.csv')
  df2 = pd.read_csv(folder + 'eurovis.csv')
  df3 = pd.read_csv(folder + 'chi-filtered.csv')

  # Combine the DataFrames vertically using concat
  combined_df = pd.concat([df1, df2, df3], axis=0, ignore_index=True)

  # Sort the combined DataFrame by "Year", "Conference", and "Title" columns
  combined_df['Title_lower'] = combined_df['Title'].str.lower()

  combined_df = combined_df.sort_values(by=['Year', 'Conference', 'Title_lower'], ascending=[False, False, True], ignore_index=True)

  # drop "Title_lower" column
  combined_df = combined_df.drop(columns=['Title_lower'])

  # Add empty column Resources to end of DataFrame
  combined_df['Resources'] = ""

  # Save the combined DataFrame to a new CSV file
  combined_df.to_csv('../../Public/data/papers.csv', index=False)


if __name__ == '__main__':
    combine()
