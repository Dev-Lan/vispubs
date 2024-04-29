# thanks chatgpt for writing 95% of this.

import pandas as pd
# Conference,Year,Title,DOI,Abstract,AuthorNames-Deduped,Award

# Load the CSV files into pandas DataFrames
df1 = pd.read_csv('VIS.csv')
df2 = pd.read_csv('eurovis.csv')
df3 = pd.read_csv('chi-filtered.csv')

# Combine the DataFrames vertically using concat
combined_df = pd.concat([df1, df2, df3], axis=0, ignore_index=True)

# Sort the combined DataFrame by "Year", "Conference", and "Title" columns
combined_df['Title_lower'] = combined_df['Title'].str.lower()

combined_df = combined_df.sort_values(by=['Year', 'Conference', 'Title_lower'], ascending=[False, False, True], ignore_index=True)

# drop "Title_lower" column
combined_df = combined_df.drop(columns=['Title_lower'])

# Save the combined DataFrame to a new CSV file
combined_df.to_csv('papers.csv', index=False)