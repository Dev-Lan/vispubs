import pandas as pd
'''
This script combines two csv files into one. Both files contain the same data, with the same column headers.
However, the rows are in a different order. The rows can be uniquely identified based on the DOI column.

The PRIMARY_INPUT_FILENAME contains most of the data, however, the AuthorNames-Deduped is not correct.
The AUTHOR_INPUT_FILENAME contains the correct DOI and AuthorNames-Deduped column.
The OUTPUT_FILENAME will contain the the merged results of these two files.
'''

PRIMARY_INPUT_FILENAME = './temp/VIS23/all-pubs.csv'
AUTHOR_INPUT_FILENAME = './temp/VIS23/all-pubs-authors.csv'
OUTPUT_FILENAME = './temp/VIS23/all-pubs-merged.csv'

def merge_csv_files(primary_file, author_file, output_file):
    # Read the primary input file
    primary_df = pd.read_csv(primary_file)

    # Read the author input file
    author_df = pd.read_csv(author_file)

    primary_df.drop('AuthorNames-Deduped', axis=1, inplace=True)

    # Add the correct author column based on the DOI column
    merged_df = pd.merge(primary_df, author_df[['DOI', 'AuthorNames-Deduped']], on='DOI')

    # rearange column order to be consistent with existing CSVs
    merged_df = merged_df[['Conference', 'Year', 'Title', 'DOI', 'Abstract', 'AuthorNames-Deduped', 'Award']]
    # Check if there are any rows that do not match
    if len(merged_df) != len(primary_df):
        print("Warning: Some rows do not match.")

    # Write the merged dataframe to the output file
    merged_df.to_csv(output_file, index=False)

# Usage example
merge_csv_files(PRIMARY_INPUT_FILENAME, AUTHOR_INPUT_FILENAME, OUTPUT_FILENAME)

