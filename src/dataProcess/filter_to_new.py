import pandas as pd
import logging

'''
Given the input file in ./temp/potential_new_papers.csv and the
existing file in ./intermediate/, filter the input file to only
include papers that are not in the existing file. Save the output to ./temp/new_papers.csv.
'''


def filter_to_new(input_file, output_file):
  logger = logging.getLogger('filter_to_new')
  # associated events (e.g. vizsec) that receive BP, and publish in TVCG in jan.
  df_assoc = pd.read_csv('./intermediate/associated_tvcg.csv')

  # Load the CSV files into pandas DataFrames
  df1 = pd.read_csv('./intermediate/VIS.csv')
  df2 = pd.read_csv('./intermediate/eurovis.csv')
  df3 = pd.read_csv('./intermediate/chi.csv') # explicitly want the non-filtered version

  # Combine the DataFrames vertically using concat
  combined_df = pd.concat([df1, df2, df3], axis=0, ignore_index=True)

  # Read the input and existing files into dataframes
  input_df = pd.read_csv(input_file)

  # Filter the input dataframe to include only papers not in the existing dataframe
  filtered_df = input_df[~input_df['DOI'].isin(combined_df['DOI'])]

  # ignore associated papers
  filtered_df = filtered_df[~filtered_df['DOI'].isin(df_assoc['DOI'])]

  # sort by conference, then by year
  filtered_df = filtered_df.sort_values(by=['Conference', 'Year'], ascending=[True, False])

  # (debugging)
  # remove Resources columns
  # filtered_df = filtered_df.drop(columns=['Resources'])
  # # remove columns with year 2024
  # filtered_df = filtered_df[filtered_df['Year'] != 2024]
  # (end debugging)

  # Save the filtered dataframe to the output file
  filtered_df.to_csv(output_file, index=False)

if __name__ == "__main__":
  input_filename = './temp/potential_new_papers.csv'
  output_filename = './temp/new_papers.csv'
  filter_to_new(input_filename, output_filename)
