import csv
import pandas as pd


'''
This filters the list of papers in a csv file by keywords. Only papers that
    include at least one of the include_keywords and
    none of the exclude_keywords are included in the output csv file.
'''

# Example usage
input_file = './intermediate/chi.csv'
output_file = './intermediate/chi-filtered.csv'



def filter_to_vis_papers(input_file, output_file):
   filter_by_keywords(input_file, output_file, include_keywords, exclude_keywords)

include_keywords = {'visualization','visualisation','visualizing', 'visualising', 'visual analytics','visual analysis','visual analyses','visual data', 'physical data', 'data physical'}
exclude_keywords = {'(abstract only)'}

def filter_by_keywords(input_file, output_file, include_keywords, exclude_keywords):
    df = pd.read_csv(input_file, quotechar='"', skipinitialspace=True)

    # Fill NaN values with empty strings
    df.fillna('', inplace=True)
    print(df)
    print(df.head())


    filtered_df = df[df['Title'].str.contains('|'.join(include_keywords), case=False) |
                    df['Abstract'].str.contains('|'.join(include_keywords), case=False)]

    filtered_df = filtered_df[~filtered_df['Title'].str.contains('|'.join(exclude_keywords), case=False) &
                            ~filtered_df['Abstract'].str.contains('|'.join(exclude_keywords), case=False)]

    # Write the filtered DataFrame to a new CSV file
    filtered_df.to_csv(output_file, index=False)


if __name__ == '__main__':
  filter_to_vis_papers(input_file, output_file)
