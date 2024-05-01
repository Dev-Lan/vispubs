import pandas as pd

'''
This python script will accept a CSV file. This CSV file has various columns, but only three are relevant:
    Year - The year a paper was published.
    Conference - The venue the paper was published. 'CHI' and 'EuroVis' should be distinct, all others should fall into 'VIS'
    Resources - a list of resource keys separated by ';', the 'P' key indicates that a paper resource exists.


This script will count the number and frequency of papersd that have a paper resource for each year and conference. It will
output three csv files, one for each conference, sorted by year.
'''


# def get_preprint_counts(csv_file):
#     # Read the CSV file into a pandas DataFrame
#     df = pd.read_csv(csv_file)
    
#     # Filter the DataFrame to include only relevant columns
#     relevant_columns = ['Year', 'Conference', 'Resources']
#     df = df[relevant_columns]

#     # Fill NaN values in 'Resources' column with an empty string
#     df['Resources'] = df['Resources'].fillna('')
    
#     # Create separate DataFrames for each conference
#     chi_df = df[df['Conference'] == 'CHI']
#     eurovis_df = df[df['Conference'] == 'EuroVis']
#     vis_df = df[df['Conference'] != 'CHI'][df['Conference'] != 'EuroVis']
    
#     # Count the number of papers with a paper resource for each year and conference
#     chi_counts = chi_df.groupby('Year')['Resources'].apply(lambda x: x.str.split(';').apply(lambda y: 'P' in y).sum())
#     eurovis_counts = eurovis_df.groupby('Year')['Resources'].apply(lambda x: x.str.split(';').apply(lambda y: 'P' in y).sum())
#     vis_counts = vis_df.groupby('Year')['Resources'].apply(lambda x: x.str.split(';').apply(lambda y: 'P' in y).sum())
    
#     # Sort the counts by year
#     chi_counts = chi_counts.sort_index()
#     eurovis_counts = eurovis_counts.sort_index()
#     vis_counts = vis_counts.sort_index()
    
#     # Output the counts to separate CSV files
#     chi_counts.to_csv('./temp/preprint_counts_chi.csv')
#     eurovis_counts.to_csv('./temp/preprint_counts_eurovis.csv')
#     vis_counts.to_csv('./temp/preprint_counts_vis.csv')

# def get_preprint_counts(csv_file):
#     # Read the CSV file into a pandas DataFrame
#     df = pd.read_csv(csv_file)
    
#     # Filter the DataFrame to include only relevant columns
#     relevant_columns = ['Year', 'Conference', 'Resources']
#     df = df[relevant_columns]

#     # Fill NaN values in 'Resources' column with an empty string
#     df['Resources'] = df['Resources'].fillna('')
    
#     # Count the number of papers with a paper resource for each year and conference
#     counts = df.groupby(['Conference', 'Year'])['Resources'].apply(lambda x: x.str.split(';').apply(lambda y: 'P' in y).sum())
    
#     # Count the total number of papers for each year and conference
#     total_counts = df.groupby(['Conference', 'Year']).size()
    
#     # Calculate the frequencies
#     frequencies = counts / total_counts
    
#     # Merge counts and frequencies into a single DataFrame
#     result = pd.DataFrame({'Counts': counts, 'Frequencies': frequencies})
    
#     # Split the result into three separate DataFrames for each conference
#     chi_result = result.xs('CHI', level='Conference')
#     eurovis_result = result.xs('EuroVis', level='Conference')
#     vis_result = result.drop(['CHI', 'EuroVis']).unstack(level=0)
    
#     # Sort the DataFrames by year
#     chi_result = chi_result.sort_index()
#     eurovis_result = eurovis_result.sort_index()
#     vis_result = vis_result.sort_index()
    
#     # Output the counts and frequencies to separate CSV files for each conference
#     chi_result.to_csv('./temp/preprint_counts_and_frequencies_chi.csv')
#     eurovis_result.to_csv('./temp/preprint_counts_and_frequencies_eurovis.csv')
#     vis_result.to_csv('./temp/preprint_counts_and_frequencies_vis.csv')
#     # Read the CSV file into a pandas DataFrame
#     df = pd.read_csv(csv_file)
    
#     # Filter the DataFrame to include only relevant columns
#     relevant_columns = ['Year', 'Conference', 'Resources']
#     df = df[relevant_columns]

#     # Fill NaN values in 'Resources' column with an empty string
#     df['Resources'] = df['Resources'].fillna('')
    
#     # Count the number of papers with a paper resource for each year and conference
#     counts = df.groupby(['Conference', 'Year'])['Resources'].apply(lambda x: x.str.split(';').apply(lambda y: 'P' in y).sum())
    
#     # Count the total number of papers for each year and conference
#     total_counts = df.groupby(['Conference', 'Year']).size()
    
#     # Calculate the frequencies
#     frequencies = counts / total_counts
    
#     # Merge counts and frequencies into a single DataFrame
#     result = pd.DataFrame({'Counts': counts, 'Frequencies': frequencies})
    
#     # Pivot the result DataFrame to have conferences as columns
#     result = result.unstack(level=0)
    
#     # Sort the result DataFrame by year
#     result = result.sort_index()
    
#     # Output the result to a CSV file
#     result.to_csv('./temp/preprint_counts_and_frequencies.csv')

def get_preprint_counts(csv_file):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)
    
    # Filter the DataFrame to include only relevant columns
    relevant_columns = ['Year', 'Conference', 'Resources']
    df = df[relevant_columns]

    # Fill NaN values in 'Resources' column with an empty string
    df['Resources'] = df['Resources'].fillna('')
    
    # Count the number of papers with a paper resource for each year and conference
    counts = df.groupby(['Conference', 'Year'])['Resources'].apply(lambda x: x.str.split(';').apply(lambda y: 'P' in y).sum())
    
    # Count the total number of papers for each year and conference
    total_counts = df.groupby(['Conference', 'Year']).size()
    
    # Calculate the frequencies
    frequencies = counts / total_counts
    
    # Merge counts and frequencies into a single DataFrame
    result = pd.DataFrame({'Counts': counts, 'Frequencies': frequencies})
    

    
  # Combine all other conferences into 'VIS'
    other_conferences_counts = counts.loc[~counts.index.get_level_values('Conference').isin(['CHI', 'EuroVis'])]
    other_conferences_total_counts = total_counts.loc[~total_counts.index.get_level_values('Conference').isin(['CHI', 'EuroVis'])]
    vis_counts = other_conferences_counts.groupby('Year').sum()
    vis_total_counts = other_conferences_total_counts.groupby('Year').sum()
    vis_frequencies = vis_counts / vis_total_counts
    
    # Create DataFrame for 'VIS' conference
    vis_result = pd.DataFrame({'Counts': vis_counts, 'Frequencies': vis_frequencies})
    
    # Split the result into three separate DataFrames for each conference
    chi_result = result.xs('CHI', level='Conference')
    eurovis_result = result.xs('EuroVis', level='Conference')

    # Sort the DataFrames by year
    chi_result = chi_result.sort_index()
    eurovis_result = eurovis_result.sort_index()
    vis_result = vis_result.sort_index()
    
    # Output the counts and frequencies to separate CSV files for each conference
    chi_result.to_csv('./temp/preprint_counts_and_frequencies_chi.csv')
    eurovis_result.to_csv('./temp/preprint_counts_and_frequencies_eurovis.csv')
    vis_result.to_csv('./temp/preprint_counts_and_frequencies_vis.csv')

get_preprint_counts('../../public/data/papers.csv')