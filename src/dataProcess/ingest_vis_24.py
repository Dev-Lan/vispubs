import pandas as pd
import json
'''
Ingesting VIS data is different because it is helpful to load it into Vispubs before the data is officially published on tvcg.


To add the data there are three relevant files in ./input/vis24/

  A. vis24_a11y_openpractices.csv -  contains links to preprrints / preregistrations / acccessible flag
  B. ieeexport.csv - early access export from ieeeexplore. most important for the DOI and abstract
  C. papers.json - useful for the full author names
'''

# Load the data from the three files
a11y_openpractices_path = './input/vis24/vis24_a11y_openpractices.csv'
ieeexport_path = './input/vis24/ieeexport.csv'
papers_json_path = './input/vis24/papers.json'

# Load both csv files into pandas data frames
a11y_openpractices_df = pd.read_csv(a11y_openpractices_path)
ieeexport_df = pd.read_csv(ieeexport_path)

# filter vis24_a11y_openpractices.csv to only include the rows where column 'Type' is 'Full'
a11y_openpractices_df = a11y_openpractices_df[a11y_openpractices_df['Type'] == 'Full']

# rename column 'Document Title' to 'Title' in 'ieeexport.csv'
ieeexport_df = ieeexport_df.rename(columns={'Document Title': 'Title'})

# combine the two dataframes on the 'Title' column
combined_df = pd.merge(a11y_openpractices_df, ieeexport_df, on='Title')

# print the dataframe
# print(combined_df)
# print(combined_df.columns)

# prepend 'v-full-' to the 'Paper ID' column in combined_df
combined_df['Paper ID'] = 'v-full-' + combined_df['Paper ID'].astype(str)

# Load the papers.json file into a pandas data frame
with open(papers_json_path, 'r') as f:
  papers_data = json.load(f)

papers_df = pd.json_normalize(papers_data)
papers_df = papers_df.rename(columns={'id': 'Paper ID'})

# print the dataframe
# print(papers_df.columns)
# print(papers_df['authors'][0])


# get the rows from a11y_openpractices_df that are not in combined_df and print them
# non_combined_df = a11y_openpractices_df[~a11y_openpractices_df['Title'].isin(combined_df['Title'])]
# print(non_combined_df[['Paper ID', 'Title']])
# temp code for fixing title changes...


# combine the two dataframes on the 'Title' column
combined_df = pd.merge(combined_df, papers_df, on='Paper ID')

# print(combined_df.columns)


combined_df['Conference'] = 'Vis'
combined_df['Year'] = 2024
combined_df = combined_df.rename(columns={'award': 'Award'})

# change award 'best' to 'BP' and 'honorable' to 'HM'
combined_df['Award'] = combined_df['Award'].apply(lambda x: 'BP' if x == 'best' else 'HM' if x == 'honorable' else x)

# print(combined_df['authors'][0][0]['name'])

# Function to extract names and join them with semicolons
def extract_names(cell):
    # Extract names
    names = [record['name'] for record in cell]
    # Join names with semicolons
    return ';'.join(names)

# Apply the function to the relevant column
combined_df['AuthorNames-Deduped'] = combined_df['authors'].apply(extract_names)


# print(combined_df['AuthorNames-Deduped'][0])

# create copy of df with only relevant columns [Conference,Year,Title,DOI,Abstract,AuthorNames-Deduped,Award,Accessibility]
vis24_df = combined_df[['Conference', 'Year', 'Title', 'DOI', 'Abstract', 'AuthorNames-Deduped', 'Award', 'Accessibility']]

# Change 'Accessible' to 'true' and in the 'Accessibility' column
vis24_df['Accessibility'] = vis24_df['Accessibility'].apply(lambda x: 'true' if x == 'Accessible' else '')
vis24_df['Early'] = 'true'

# save the dataframe to a csv file
vis24_df.to_csv('./temp/vis24.csv', index=False)

# save resources to new file type for ingestion

# print(combined_df.columns)
# create copy of df with only relevant resource columns [DOI, Paper ID, Supplemtal Material Link, Preprint Link, Pre-registration]
resource_df = combined_df[['DOI', 'Paper ID', 'Supplemental Material Link', 'Preprint Link', 'Pre-registration']]

# add the content URL by prepending 'https://ieeevis.org/year/2024/program/paper_' and adding '.html' to the 'Paper ID' column in resource_df
resource_df['VIS_URL'] = 'https://ieeevis.org/year/2024/program/paper_' + resource_df['Paper ID'] + '.html'

# print(resource_df)
# Expand into long table format with four columns [DOI, icon, name, url]
# where icon is one of 'Supplemental', 'Preprint', 'Prereg', 'VIS URL'
# and name is the same as icon and url is the corresponding link

# Create a list to hold the expanded rows
expanded_rows = []

# Iterate over each row in the resource_df
for _, row in resource_df.iterrows():
  # Append the preprint link
  if pd.notna(row['Preprint Link']):
    expanded_rows.append({
      'DOI': row['DOI'],
      'icon': 'paper',
      'name': 'Paper Preprint',
      'url': row['Preprint Link']
    })
  # Append the supplemental material link
  if pd.notna(row['Supplemental Material Link']):
    expanded_rows.append({
      'DOI': row['DOI'],
      'icon': 'other',
      'name': 'Supplemental Material',
      'url': row['Supplemental Material Link']
    })
  # Append the pre-registration link
  if pd.notna(row['Pre-registration']):
    prereg_list = row['Pre-registration'].split(';')
    for prereg in prereg_list:
      if '|' in prereg:
        label, url = prereg.split('|')
      else:
        label = 'Preregistration'
        url = prereg
      expanded_rows.append({
        'DOI': row['DOI'],
        'icon': 'other',
        'name': label,
        'url': url
      })
  # Append the VIS URL
  if pd.notna(row['VIS_URL']):
    expanded_rows.append({
      'DOI': row['DOI'],
      'icon': 'other',
      'name': 'IEEE VIS Conference Page',
      'url': row['VIS_URL']
    })

# Convert the list of expanded rows into a DataFrame
expanded_df = pd.DataFrame(expanded_rows)

# Print the first few rows of the expanded DataFrame
pd.set_option("display.max_columns", None)
print(expanded_df)
# save the expanded_df to a csv file
expanded_df.to_csv('./temp/vis24_resources.csv', index=False)
