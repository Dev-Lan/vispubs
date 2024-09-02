import pandas as pd
'''
For consistency, load csv into pandas and export it back to csv. This only contains quotes on titles that contain commas.
'''

csv_data = pd.read_csv('chi.csv')
csv_data.to_csv('chi-quoted.csv', index=False)

